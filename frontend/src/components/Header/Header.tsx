import githubIcon from "../../assets/react.svg";

interface HeaderItem {
  label: string;
  link: string;
  icon: string;
}

const HEADER_RIGHT_ITEMS: HeaderItem[] = [
  {
    label: "GitHub",
    link: "https://github.com",
    icon: githubIcon,
  },
];

const Header = () => {
  return (
    <header className="flex items-center justify-between w-[95%] h-14 mx-auto mt-4 py-2 bg-gray-600 px-4 shadow-md rounded-full">
      <div className="text-lg font-bold">Pose Annotator</div>
      {HEADER_RIGHT_ITEMS.map((item) => {
        return (
          <a
            key={item.label}
            href={item.link}
            className="ml-4 flex items-center hover:underline"
          >
            <img src={item.icon} alt={item.label} className="w-5 h-5 mr-2" />
          </a>
        );
      })}
    </header>
  );
};

export default Header;
