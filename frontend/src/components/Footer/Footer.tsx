const CURRENT_YEAR = new Date().getFullYear();
const COPYRIGHT_DISCLOSURE = `Copyright © ${CURRENT_YEAR} Tim Lun Chen & Natasha Yamane`;
const LICENSE_LINK = "https://opensource.org/licenses/MIT";
const LICENSE_DISCLOSURE = () => {
  return (
    <p>
      Licensed under the{" "}
      <a
        className="text-[#B8E6D5] underline"
        href={LICENSE_LINK}
        target="_blank"
        rel="noopener noreferrer"
      >
        MIT License
      </a>
      .
    </p>
  );
};

const Footer = () => {
  return (
    <footer className="w-full p-4 text-center text-sm text-gray-300">
      <p>{COPYRIGHT_DISCLOSURE}</p>
      <LICENSE_DISCLOSURE />
    </footer>
  );
};

export default Footer;
