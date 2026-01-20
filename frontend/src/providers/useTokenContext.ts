import { useContext } from "react";
import { TokenContext } from "./TokenProvider";

const useTokenContext = () => {
  const token = useContext(TokenContext);

  return token;
};

export default useTokenContext;
