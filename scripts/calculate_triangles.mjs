import * as THREE from "three";

function countTriangles(geom) {
  if (geom.index) {
    return geom.index.count / 3;
  }
  return geom.attributes.position.count / 3;
}

// Junior Dev Geometry Count
function getJuniorDevTriangles() {
  let count = 0;
  // Torso
  count += countTriangles(new THREE.CylinderGeometry(0.78, 1.05, 1.15, 8));
  // Hoodie collar
  count += countTriangles(new THREE.TorusGeometry(0.34, 0.10, 6, 12));
  // 2 Drawstrings
  count += 2 * countTriangles(new THREE.CylinderGeometry(0.012, 0.012, 0.28, 6));
  // Arms: 2 arms * (upper + forearm + hand)
  // upper arm (box)
  count += 2 * countTriangles(new THREE.BoxGeometry(0.26, 0.70, 0.26));
  // forearm (box)
  count += 2 * countTriangles(new THREE.BoxGeometry(0.22, 0.60, 0.22));
  // hand (box)
  count += 2 * countTriangles(new THREE.BoxGeometry(0.18, 0.18, 0.14));
  // Neck
  count += countTriangles(new THREE.CylinderGeometry(0.22, 0.25, 0.36, 8));
  // Skull
  count += countTriangles(new THREE.IcosahedronGeometry(0.62, 1));
  // Chin
  count += countTriangles(new THREE.BoxGeometry(0.26, 0.14, 0.22));
  // Jaw left & right
  count += 2 * countTriangles(new THREE.BoxGeometry(0.18, 0.14, 0.28));
  // Nose
  count += countTriangles(new THREE.ConeGeometry(0.07, 0.18, 5));
  // Ears (dodecahedron detail 0 = 36 tris)
  count += 2 * countTriangles(new THREE.DodecahedronGeometry(0.14, 0));
  // Hair base
  count += countTriangles(new THREE.SphereGeometry(0.66, 8, 6, 0, Math.PI * 2, 0, Math.PI * 0.58));
  // Hair messy clusters (5 cones detail 4)
  count += countTriangles(new THREE.ConeGeometry(0.13, 0.32, 4));
  count += countTriangles(new THREE.ConeGeometry(0.14, 0.34, 4));
  count += countTriangles(new THREE.ConeGeometry(0.12, 0.30, 4));
  count += countTriangles(new THREE.ConeGeometry(0.15, 0.35, 4));
  count += countTriangles(new THREE.ConeGeometry(0.14, 0.32, 4));
  // Stubble (chin + 2 jaw quads)
  count += countTriangles(new THREE.BoxGeometry(0.27, 0.13, 0.21));
  count += 2 * countTriangles(new THREE.BoxGeometry(0.19, 0.13, 0.27));
  // Spectacles: 2 frames + bridge
  count += 2 * countTriangles(new THREE.BoxGeometry(0.24, 0.15, 0.02));
  count += countTriangles(new THREE.BoxGeometry(0.14, 0.02, 0.02));
  // Eyes: 2 * (sclera + pupil + top eyelid + bottom eyelid)
  count += 2 * countTriangles(new THREE.SphereGeometry(0.075, 8, 8));
  count += 2 * countTriangles(new THREE.SphereGeometry(0.038, 6, 6));
  count += 2 * countTriangles(new THREE.BoxGeometry(0.16, 0.075, 0.04)); // top eyelid
  count += 2 * countTriangles(new THREE.BoxGeometry(0.16, 0.075, 0.04)); // bottom eyelid
  // Eyebrows (2 boxes)
  count += 2 * countTriangles(new THREE.BoxGeometry(0.22, 0.05, 0.03));
  // Mouth cavity + upper teeth
  count += countTriangles(new THREE.BoxGeometry(0.20, 0.05, 0.06));
  count += countTriangles(new THREE.BoxGeometry(0.15, 0.024, 0.02));

  return count;
}

// Indian Dad Geometry Count
function getDadTriangles() {
  let count = 0;
  // Torso
  count += countTriangles(new THREE.CylinderGeometry(0.78, 1.05, 1.15, 8));
  // Polo collar
  count += countTriangles(new THREE.TorusGeometry(0.34, 0.10, 6, 12));
  // Polo placket
  count += countTriangles(new THREE.BoxGeometry(0.16, 0.36, 0.04));
  // 3 Buttons
  count += 3 * countTriangles(new THREE.CylinderGeometry(0.018, 0.018, 0.02, 6));
  // Arms: 2 arms * (upper + forearm + hand)
  count += 2 * countTriangles(new THREE.BoxGeometry(0.26, 0.70, 0.26));
  count += 2 * countTriangles(new THREE.BoxGeometry(0.22, 0.60, 0.22));
  count += 2 * countTriangles(new THREE.BoxGeometry(0.18, 0.18, 0.14));
  // Neck
  count += countTriangles(new THREE.CylinderGeometry(0.22, 0.25, 0.36, 8));
  // Skull
  count += countTriangles(new THREE.IcosahedronGeometry(0.62, 1));
  // Chin
  count += countTriangles(new THREE.BoxGeometry(0.26, 0.14, 0.22));
  // Jaw left & right
  count += 2 * countTriangles(new THREE.BoxGeometry(0.18, 0.14, 0.28));
  // Nose
  count += countTriangles(new THREE.ConeGeometry(0.07, 0.18, 5));
  // Ears (dodecahedron)
  count += 2 * countTriangles(new THREE.DodecahedronGeometry(0.14, 0));
  // Hair base
  count += countTriangles(new THREE.SphereGeometry(0.66, 8, 6, 0, Math.PI * 2, 0, Math.PI * 0.58));
  // Side-part ridge
  count += countTriangles(new THREE.BoxGeometry(0.54, 0.08, 0.42));
  // Grey temple highlights (2 boxes)
  count += 2 * countTriangles(new THREE.BoxGeometry(0.12, 0.22, 0.32));
  // Reading Spectacles (2 torus + bridge)
  count += 2 * countTriangles(new THREE.TorusGeometry(0.11, 0.02, 6, 12));
  count += countTriangles(new THREE.BoxGeometry(0.14, 0.02, 0.02));
  // Eyes: 2 * (sclera + pupil + top eyelid + bottom eyelid)
  count += 2 * countTriangles(new THREE.SphereGeometry(0.075, 8, 8));
  count += 2 * countTriangles(new THREE.SphereGeometry(0.038, 6, 6));
  count += 2 * countTriangles(new THREE.BoxGeometry(0.16, 0.075, 0.04));
  count += 2 * countTriangles(new THREE.BoxGeometry(0.16, 0.075, 0.04));
  // Eyebrows (2 boxes)
  count += 2 * countTriangles(new THREE.BoxGeometry(0.22, 0.05, 0.03));
  // Mustache (center + 2 curved wings)
  count += countTriangles(new THREE.BoxGeometry(0.34, 0.09, 0.08));
  count += 2 * countTriangles(new THREE.BoxGeometry(0.10, 0.06, 0.06));
  // Mouth cavity + upper teeth
  count += countTriangles(new THREE.BoxGeometry(0.20, 0.05, 0.06));
  count += countTriangles(new THREE.BoxGeometry(0.15, 0.024, 0.02));

  return count;
}

// AI Orb Geometry Count
function getAIOrbTriangles(type) {
  let count = 0;
  // Orb chassis: IcosahedronGeometry(1.0, 1) = 80 tris
  count += countTriangles(new THREE.IcosahedronGeometry(1.0, 1));
  // Bezel ring: CylinderGeometry(0.60, 0.60, 0.14, 16)
  count += countTriangles(new THREE.CylinderGeometry(0.60, 0.60, 0.14, 16));
  // Screen: CylinderGeometry(0.54, 0.54, 0.02, 24)
  count += countTriangles(new THREE.CylinderGeometry(0.54, 0.54, 0.02, 24));
  // Eyes: 2 boxes
  count += 2 * countTriangles(new THREE.BoxGeometry(0.15, 0.09, 0.02));
  // 7-bar equalizer mouth: 7 boxes
  count += 7 * countTriangles(new THREE.BoxGeometry(0.045, 0.10, 0.02));
  // Translucent Halo ring: TorusGeometry(1.30, 0.018, 6, 24)
  count += countTriangles(new THREE.TorusGeometry(1.30, 0.018, 6, 24));

  if (type === "claude") {
    // 2 swept-back antennas (cylinder 6 + sphere 6x6)
    count += 2 * countTriangles(new THREE.CylinderGeometry(0.03, 0.04, 0.38, 6));
    count += 2 * countTriangles(new THREE.SphereGeometry(0.07, 6, 6));
  } else if (type === "gemini" || type === "antigravity_bot") {
    // 1 top antenna stalk (cylinder 6) + 1 plasma orb (sphere 8x8)
    count += countTriangles(new THREE.CylinderGeometry(0.035, 0.045, 0.35, 6));
    count += countTriangles(new THREE.SphereGeometry(0.10, 8, 8));
    // 2 side acoustic ear bolts (cylinder 6)
    count += 2 * countTriangles(new THREE.CylinderGeometry(0.16, 0.22, 0.16, 6));
  } else if (type === "grok") {
    // 2 cyber horns (cone detail 4)
    count += 2 * countTriangles(new THREE.ConeGeometry(0.08, 0.46, 4));
  }

  return count;
}

console.log("=== EXACT THREE.JS TRIANGLE COUNT PER CHARACTER ===");
console.log("junior_dev:      ", getJuniorDevTriangles(), "triangles");
console.log("dad:             ", getDadTriangles(), "triangles");
console.log("claude:          ", getAIOrbTriangles("claude"), "triangles");
console.log("gemini:          ", getAIOrbTriangles("gemini"), "triangles");
console.log("grok:            ", getAIOrbTriangles("grok"), "triangles");
console.log("antigravity_bot: ", getAIOrbTriangles("antigravity_bot"), "triangles");
