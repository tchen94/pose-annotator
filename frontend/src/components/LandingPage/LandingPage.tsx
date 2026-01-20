import { Link } from "react-router-dom";
import logo from "../../assets/logo.png";
import GithubIcon from "../../assets/github.svg";

const LandingPage = () => {
  return (
    <div className="w-full h-full bg-[#242424] relative">
      {/* GitHub Link - Top Right */}
      <div className="absolute top-6 right-6">
        <a
          href="https://github.com/tchen94/pose-annotator/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-400 hover:text-white transition-colors"
        >
          <img
            src={GithubIcon}
            alt="GitHub"
            className="w-10 h-10 mr-2 invert"
          />
        </a>
      </div>

      {/* Main Content */}
      <div className="w-full h-full flex items-center justify-center">
        <div className="max-w-2xl mx-auto text-center px-8">
          {/* Logo */}
          <img
            src={logo}
            alt="Pose Annotator"
            className="mx-auto object-contain"
          />

          <p className="text-gray-400 text-2xl mt-6 mb-12">
            Precision annotation for human pose estimation
          </p>

          {/* CTA Button */}
          <Link
            to="/get-access"
            className="inline-block bg-[#B8E6D5] text-[#242424] font-extrabold px-8 py-4 rounded-lg hover:bg-[#A3D9C7] transition-colors"
          >
            Get Started
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
