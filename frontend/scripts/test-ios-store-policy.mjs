/**
 * Pure checks for iOS App Store listing policy (no Capacitor / DOM).
 * Run: node frontend/scripts/test-ios-store-policy.mjs
 */
import assert from "node:assert/strict";
import { googleSignInAllowed } from "../src/iosStorePolicy.js";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

assert.equal(googleSignInAllowed("web", false), true);
assert.equal(googleSignInAllowed("android", false), true);
assert.equal(googleSignInAllowed("ios", false), false);
assert.equal(googleSignInAllowed("ios", true), true);

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const plist = readFileSync(join(root, "frontend/ios/App/App/Info.plist"), "utf8");
assert.match(plist, /ITSAppUsesNonExemptEncryption/);
assert.match(plist, /NSMicrophoneUsageDescription/);
assert.match(plist, /NSCameraUsageDescription/);
assert.doesNotMatch(plist, /armv7/);
assert.match(plist, /arm64/);

const privacy = readFileSync(join(root, "frontend/src/pages/Privacy.jsx"), "utf8");
assert.match(privacy, /Delete your account in the app/);
assert.match(privacy, /Live Talk/);

const info = readFileSync(join(root, "brand/mobile/APP-STORE-IOS.md"), "utf8");
assert.match(info, /com\.baratx\.app/);
assert.match(info, /https:\/\/barathx\.com\/privacy/);
assert.match(info, /1320×2868|1320x2868/);
assert.match(info, /Sign in with Apple/);
assert.match(info, /review@barathx\.com/);

const pbx = readFileSync(join(root, "frontend/ios/App/App.xcodeproj/project.pbxproj"), "utf8");
assert.match(pbx, /TARGETED_DEVICE_FAMILY = 1/);
assert.match(pbx, /PrivacyInfo.xcprivacy/);
assert.match(pbx, /PRODUCT_BUNDLE_IDENTIFIER = com.baratx.app/);

const manifest = readFileSync(join(root, "frontend/ios/App/App/PrivacyInfo.xcprivacy"), "utf8");
assert.match(manifest, /NSPrivacyTracking/);
assert.match(manifest, /NSPrivacyCollectedDataTypeEmailAddress/);
assert.match(manifest, /NSPrivacyAccessedAPICategoryUserDefaults/);

const icon = readFileSync(
  join(root, "frontend/ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png")
);
assert.deepEqual(
  [...icon.subarray(0, 8)],
  [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]
);
const width = icon.readUInt32BE(16);
const height = icon.readUInt32BE(20);
const colorType = icon[25];
assert.equal(width, 1024);
assert.equal(height, 1024);
assert.notEqual(colorType, 6, "App Store icon must not have an alpha channel");

console.log("ios store policy checks passed");
