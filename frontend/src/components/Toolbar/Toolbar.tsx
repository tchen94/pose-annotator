import testSVG from "../../assets/react.svg";

interface CanvasControl {
  label: string;
  className: string;
  icon: string;
}

const CANVAS_CONTROLS: CanvasControl[] = [
  {
    label: "Step Back",
    className: "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600",
    icon: testSVG,
  },
  {
    label: "Step Forward",
    className: "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600",
    icon: testSVG,
  },
  {
    label: "Annotate",
    className: "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600",
    icon: testSVG,
  },
  {
    label: "Undo",
    className: "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600",
    icon: testSVG,
  },
  {
    label: "Export",
    className: "px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600",
    icon: testSVG,
  },
];

const Toolbar = () => {
  return (
    <div className="flex flex-col items-center justify-between w-[90%] mx-auto mt-6 py-2 px-4">
      <div className="flex space-x-2 p-4 bg-gray-300 rounded-lg">
        {CANVAS_CONTROLS.map((control) => (
          <button
            key={control.label}
            className={control.className}
            title={control.label}
          >
            <img src={control.icon} alt={control.label} className="w-5 h-5" />
          </button>
        ))}
      </div>
    </div>
  );
};

export default Toolbar;
