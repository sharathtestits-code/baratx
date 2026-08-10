import { useEffect, useRef } from "react";
import { spacesApi } from "../api";

const ICE_SERVERS = [
  { urls: "stun:stun.l.google.com:19302" },
  { urls: "stun:stun1.l.google.com:19302" },
];

function iceConfig() {
  const servers = [...ICE_SERVERS];
  const turnUrl = (import.meta.env.VITE_TURN_URL || "").trim();
  const turnUser = (import.meta.env.VITE_TURN_USERNAME || "").trim();
  const turnPass = (import.meta.env.VITE_TURN_CREDENTIAL || "").trim();
  if (turnUrl) {
    servers.push({
      urls: turnUrl,
      username: turnUser || undefined,
      credential: turnPass || undefined,
    });
  }
  return { iceServers: servers };
}

/**
 * WebRTC mesh for Live Talk — publishes local mic/cam and plays remote audio.
 * Signaling goes through REST (/talk/signals); no SFU required for small rooms.
 */
export function useLiveTalkRtc({
  spaceId,
  token,
  myUserId,
  inTalk,
  participants,
  localStream,
  myMuted,
}) {
  const peersRef = useRef(new Map()); // peerId -> { pc, audioEl, makingOffer, ignoreOffer }
  const streamRef = useRef(localStream);
  const mutedRef = useRef(myMuted);
  const myIdRef = useRef(myUserId);
  const audioRootRef = useRef(null);

  streamRef.current = localStream;
  mutedRef.current = myMuted;
  myIdRef.current = myUserId;

  useEffect(() => {
    let root = document.getElementById("live-talk-remote-audio");
    if (!root) {
      root = document.createElement("div");
      root.id = "live-talk-remote-audio";
      root.setAttribute("aria-hidden", "true");
      root.style.cssText = "position:absolute;width:0;height:0;overflow:hidden;";
      document.body.appendChild(root);
    }
    audioRootRef.current = root;
    return () => {
      // keep root for remounts within the same page session
    };
  }, []);

  function ensureAudioEl(peerId) {
    const root = audioRootRef.current || document.body;
    let el = root.querySelector(`audio[data-peer="${peerId}"]`);
    if (!el) {
      el = document.createElement("audio");
      el.dataset.peer = peerId;
      el.autoplay = true;
      el.playsInline = true;
      el.setAttribute("playsinline", "true");
      // Must NOT be muted — this is how we hear others
      el.muted = false;
      el.volume = 1;
      root.appendChild(el);
    }
    return el;
  }

  async function sendSignal(toUserId, kind, payloadObj) {
    if (!token || !spaceId) return;
    try {
      await spacesApi.talkSignal(token, spaceId, {
        to_user_id: toUserId,
        kind,
        payload: JSON.stringify(payloadObj),
      });
    } catch {
      // Peer may have left mid-handshake
    }
  }

  function attachLocalTracks(pc) {
    const stream = streamRef.current;
    if (!stream) return;
    const senders = pc.getSenders();
    const haveAudio = senders.some((s) => s.track && s.track.kind === "audio");
    const haveVideo = senders.some((s) => s.track && s.track.kind === "video");
    stream.getAudioTracks().forEach((track) => {
      track.enabled = !mutedRef.current;
      if (!haveAudio) pc.addTrack(track, stream);
    });
    stream.getVideoTracks().forEach((track) => {
      if (!haveVideo) pc.addTrack(track, stream);
    });
  }

  function syncLocalMuteOnPeers() {
    const enabled = !mutedRef.current;
    peersRef.current.forEach(({ pc }) => {
      pc.getSenders().forEach((sender) => {
        if (sender.track && sender.track.kind === "audio") {
          sender.track.enabled = enabled;
        }
      });
    });
    if (streamRef.current) {
      streamRef.current.getAudioTracks().forEach((tr) => {
        tr.enabled = enabled;
      });
    }
  }

  async function createPeer(peerId) {
    if (peersRef.current.has(peerId)) return peersRef.current.get(peerId);
    const pc = new RTCPeerConnection(iceConfig());
    const audioEl = ensureAudioEl(peerId);
    const entry = { pc, audioEl, makingOffer: false, ignoreOffer: false };
    peersRef.current.set(peerId, entry);

    pc.onicecandidate = (ev) => {
      if (!ev.candidate) return;
      sendSignal(peerId, "ice", ev.candidate.toJSON());
    };

    pc.ontrack = (ev) => {
      const [stream] = ev.streams;
      if (!stream) return;
      audioEl.srcObject = stream;
      const play = () => {
        audioEl.play().catch(() => {
          // Autoplay may block until a click — Join / Unmute provides gesture
        });
      };
      play();
      audioEl.onloadedmetadata = play;
    };

    pc.onconnectionstatechange = () => {
      if (pc.connectionState === "failed" || pc.connectionState === "closed") {
        // Leave cleanup handles full teardown; failed may recover via ICE restart later
      }
    };

    attachLocalTracks(pc);
    return entry;
  }

  async function ensureOffer(peerId) {
    const myId = myIdRef.current;
    if (!myId || myId >= peerId) return; // only lower id initiates
    const entry = await createPeer(peerId);
    const { pc } = entry;
    if (entry.makingOffer || pc.signalingState !== "stable") return;
    try {
      entry.makingOffer = true;
      attachLocalTracks(pc);
      const offer = await pc.createOffer({ offerToReceiveAudio: true, offerToReceiveVideo: true });
      await pc.setLocalDescription(offer);
      await sendSignal(peerId, "offer", pc.localDescription);
    } catch {
      // ignore
    } finally {
      entry.makingOffer = false;
    }
  }

  async function handleSignal(signal) {
    const peerId = signal.from_user_id;
    let payload;
    try {
      payload = JSON.parse(signal.payload);
    } catch {
      return;
    }
    const entry = await createPeer(peerId);
    const { pc } = entry;
    const polite = (myIdRef.current || "") < peerId;

    try {
      if (signal.kind === "offer") {
        const offerCollision =
          entry.makingOffer || pc.signalingState !== "stable";
        entry.ignoreOffer = !polite && offerCollision;
        if (entry.ignoreOffer) return;
        await pc.setRemoteDescription(payload);
        attachLocalTracks(pc);
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        await sendSignal(peerId, "answer", pc.localDescription);
      } else if (signal.kind === "answer") {
        if (pc.signalingState === "have-local-offer") {
          await pc.setRemoteDescription(payload);
        }
      } else if (signal.kind === "ice") {
        try {
          await pc.addIceCandidate(payload);
        } catch {
          if (!entry.ignoreOffer) {
            // candidate before remote description — usually recoverable
          }
        }
      }
    } catch {
      // Bad SDP / race — next poll may renegotiate
    }
  }

  function closePeer(peerId) {
    const entry = peersRef.current.get(peerId);
    if (!entry) return;
    try {
      entry.pc.close();
    } catch {
      // ignore
    }
    if (entry.audioEl) {
      entry.audioEl.srcObject = null;
      entry.audioEl.remove();
    }
    peersRef.current.delete(peerId);
  }

  function closeAll() {
    Array.from(peersRef.current.keys()).forEach(closePeer);
  }

  // Sync peer set from participant list
  useEffect(() => {
    if (!inTalk || !myUserId || !token || !spaceId) {
      closeAll();
      return undefined;
    }
    const others = (participants || [])
      .map((p) => p.user?.id)
      .filter((id) => id && id !== myUserId);

    // Drop peers who left
    Array.from(peersRef.current.keys()).forEach((id) => {
      if (!others.includes(id)) closePeer(id);
    });

    // Create / offer to new peers
    others.forEach((id) => {
      ensureOffer(id);
    });

    return undefined;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inTalk, myUserId, token, spaceId, participants]);

  // Local mute → sender tracks
  useEffect(() => {
    if (!inTalk) return;
    syncLocalMuteOnPeers();
  }, [inTalk, myMuted, localStream]);

  // When mic stream appears after peers already connected, add tracks + re-offer
  useEffect(() => {
    if (!inTalk || !localStream || !myUserId) return;
    peersRef.current.forEach(async (entry, peerId) => {
      attachLocalTracks(entry.pc);
      const myId = myIdRef.current;
      if (!myId || myId >= peerId) return;
      if (entry.pc.signalingState !== "stable" || entry.makingOffer) return;
      try {
        entry.makingOffer = true;
        const offer = await entry.pc.createOffer({
          offerToReceiveAudio: true,
          offerToReceiveVideo: true,
        });
        await entry.pc.setLocalDescription(offer);
        await sendSignal(peerId, "offer", entry.pc.localDescription);
      } catch {
        // ignore
      } finally {
        entry.makingOffer = false;
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inTalk, localStream, myUserId]);

  // Poll signals
  useEffect(() => {
    if (!inTalk || !token || !spaceId) return undefined;
    let cancelled = false;

    async function poll() {
      try {
        const signals = await spacesApi.talkSignals(token, spaceId);
        if (cancelled || !Array.isArray(signals)) return;
        for (const signal of signals) {
          await handleSignal(signal);
        }
      } catch {
        // ignore transient
      }
    }

    poll();
    const t = setInterval(poll, 1000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inTalk, token, spaceId, myUserId]);

  // Teardown on leave / unmount
  useEffect(() => {
    if (!inTalk) closeAll();
    return () => closeAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inTalk]);

  return { resumeRemoteAudio: () => {
    peersRef.current.forEach(({ audioEl }) => {
      if (audioEl?.srcObject) audioEl.play().catch(() => {});
    });
  } };
}
