import GitHubICon from "../../assets/github.svg";
import Logo from "../../assets/logo.png";

interface HeaderItem {
  label: string;
  link: string;
  icon: string;
}

const HEADER_RIGHT_ITEMS: HeaderItem[] = [
  {
    label: "GitHub",
    link: "https://github.com/tchen94/pose-annotator/",
    icon: GitHubICon,
  },
];

const Header = () => {
  return (
    <header className="flex items-center justify-between w-[95%] h-14 mx-auto mx-18 mt-4 py-2 pt-6">
      <div className="text-2xl font-bold">
        <img
          src={Logo}
          alt="Logo"
          className="h-8 inline mr-2 transform scale-200 ml-14"
        />
      </div>
      {HEADER_RIGHT_ITEMS.map((item) => {
        return (
          <a
            key={item.label}
            href={item.link}
            className="ml-4 flex items-center hover:underline"
          >
            <img
              src={item.icon}
              alt={item.label}
              className="w-7 h-7 mr-2 invert"
            />
          </a>
        );
      })}
    </header>
  );
};

export default Header;
