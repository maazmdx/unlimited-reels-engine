import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(2);

// Enable SwiftShader ANGLE for headless CPU Three.js rendering
Config.setChromiumOpenGlRenderer("angle");
Config.setChromiumFlags({
  "use-gl": "angle",
  "use-angle": "swiftshader",
  "enable-webgl": true,
  "no-sandbox": true,
});
