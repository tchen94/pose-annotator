import { useContext } from "react";

import { VideoContext } from "../providers/VideoProvider";

const useVideoContext = () => {
  return useContext(VideoContext);
};

export default useVideoContext;
