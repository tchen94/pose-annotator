const BODY_PART = [
  "Nose",
  "Left Eye",
  "Right Eye",
  "Left Ear",
  "Right Ear",
  "Left Shoulder",
  "Right Shoulder",
  "Left Elbow",
  "Right Elbow",
  "Left Wrist",
  "Right Wrist",
  "Left Hip",
  "Right Hip",
  "Left Knee",
  "Right Knee",
  "Left Ankle",
  "Right Ankle",
];

const CheckList = () => {
  return (
    <div className="mx-auto m-4">
      <div className="overflow-y-auto border border-gray-400">
        <table className="table-auto border-collapse w-full">
          <thead className="sticky top-0">
            <tr className="bg-gray-400">
              <th className="px-4 py-2">Body Part</th>
              <th className="px-4 py-2">Visible</th>
            </tr>
          </thead>
          <tbody>
            {BODY_PART.map((part) => {
              return (
                <tr key={part} className="border-t border-gray-300">
                  <td className="px-4 py-2">{part}</td>
                  <td className="px-4 py-2 text-center">
                    <input type="checkbox" />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CheckList;
