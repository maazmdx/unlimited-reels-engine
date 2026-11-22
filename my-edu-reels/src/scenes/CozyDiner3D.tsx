import React from "react";
import { CozyDiner3D as BaseCozyDiner3D, CozyDiner3DProps } from "../components/environments3d/CozyDiner3D";

export type { CozyDiner3DProps };
export const CozyDiner3D: React.FC<CozyDiner3DProps> = (props) => {
  return <BaseCozyDiner3D {...props} />;
};
export default CozyDiner3D;
