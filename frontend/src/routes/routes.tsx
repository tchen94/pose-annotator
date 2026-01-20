import { Routes, Route } from "react-router-dom";
import GetAccessPage from "../components/GetAccessPage/GetAccessPage";
import AnnotatorPage from "../components/AnnotatorPage/AnnotatorPage";
import LandingPage from "../components/LandingPage/LandingPage";

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/get-access" element={<GetAccessPage />} />
      <Route path="/annotate/:token" element={<AnnotatorPage />} />
      <Route path="/" element={<LandingPage />} />
    </Routes>
  );
};

export default AppRoutes;
