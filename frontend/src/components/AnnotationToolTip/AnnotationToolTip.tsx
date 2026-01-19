interface AnnotationToolTipProps {
  selectedBodyPart: string;
  setSelectedBodyPart: (bodyPart: string) => void;
  handleConfirmAnnotation: () => void;
  handleCancelAnnotation: () => void;
  bodyParts: string[];
}

const AnnotationToolTip = ({
  selectedBodyPart,
  setSelectedBodyPart,
  handleConfirmAnnotation,
  handleCancelAnnotation,
  bodyParts,
}: AnnotationToolTipProps) => {
  return (
    <div className="bg-white border border-gray-400 rounded-lg shadow-lg p-4">
      <div className="space-y-3">
        <label className="block text-md font-medium text-gray-700">
          Body Part:
        </label>
        <select
          value={selectedBodyPart}
          onChange={(e) => setSelectedBodyPart(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-auto text-gray-700 text-md"
        >
          <option value="" className="text-gray-400">
            Select
          </option>
          {bodyParts.map((part) => (
            <option key={part} value={part} className="text-gray-700">
              {part}
            </option>
          ))}
        </select>
        <div className="flex gap-2">
          <button
            onClick={handleConfirmAnnotation}
            disabled={!selectedBodyPart}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Ok
          </button>
          <button
            onClick={handleCancelAnnotation}
            className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnnotationToolTip;
