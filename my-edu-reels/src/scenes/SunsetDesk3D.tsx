import React from "react";
import { SunsetDesk3D as BaseSunsetDesk3D, SunsetDesk3DProps } from "../components/environments3d/SunsetDesk3D";

export type { SunsetDesk3DProps };
export const SunsetDesk3D: React.FC<SunsetDesk3DProps> = (props) => {
  return <BaseSunsetDesk3D {...props} />;
};
export default SunsetDesk3D;
