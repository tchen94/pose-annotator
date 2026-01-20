import useVideoContext from "../../providers/useVideoContext";
import { BODY_PART } from "../../constants/constants";
import PendingIcon from "../../assets/pending.svg";
import DoneIcon from "../../assets/done.svg";
import TrashIcon from "../../assets/trash.svg";

const CheckList = () => {
  const { videoData, annotations, currentFrameNumber, setAnnotations } =
    useVideoContext();

  const isDone = (bodyPart: string) => {
    const frameAnnotations = annotations[currentFrameNumber];
    if (!frameAnnotations || !frameAnnotations[bodyPart]) return false;

    const { x, y, not_visible } = frameAnnotations[bodyPart];
    return (x && y && !not_visible) || not_visible;
  };

  const setIcon = (bodyPart: string) => {
    if (isDone(bodyPart)) {
      return DoneIcon;
    }

    return PendingIcon;
  };

  const toggleNotVisible = (bodyPart: string) => {
    const frameAnnotations = annotations[currentFrameNumber];
    if (!frameAnnotations || !frameAnnotations[bodyPart]) return;

    const { not_visible } = frameAnnotations[bodyPart];
    setAnnotations({
      ...annotations,
      [currentFrameNumber]: {
        ...annotations[currentFrameNumber],
        [bodyPart]: {
          ...annotations[currentFrameNumber][bodyPart],
          not_visible: !not_visible,
        },
      },
    });
  };

  const resetAnnotation = (bodyPart: string) => {
    if (!annotations[currentFrameNumber]) return;

    setAnnotations({
      ...annotations,
      [currentFrameNumber]: {
        ...annotations[currentFrameNumber],
        [bodyPart]: {
          x: null,
          y: null,
          not_visible: false,
        },
      },
    });
  };

  return (
    <>
      {videoData && (
        <div>
          <div className="checklist-container overflow-y-auto h-fit border border-gray-500 mr-2 rounded-lg mt-18">
            <table className="table-auto border-collapse">
              <thead className="sticky top-0">
                <tr className="bg-gray-600">
                  <th className="px-4 py-2 flex justify-start">Body Part</th>
                  <th className="px-4 py-2">Annotation</th>
                  <th className="px-4 py-2">Not Visible</th>
                </tr>
              </thead>
              <tbody>
                {BODY_PART.map((part) => {
                  return (
                    <tr key={part} className="border-t border-gray-500">
                      <td className="px-4 py-2">{part}</td>
                      <td className="px-4 py-2 text-center">
                        <div className="flex flex-row justify-start items-center gap-1 w-[60px] mx-auto">
                          <img
                            src={setIcon(part)}
                            alt={part}
                            className="w-6 h-6"
                          />
                          {isDone(part) && (
                            <img
                              src={TrashIcon}
                              alt="trash"
                              className="w-5 h-5 hover:cursor-pointer"
                              onClick={() => resetAnnotation(part)}
                            />
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-2 text-center">
                        <input
                          className="border-white hover:cursor-pointer disabled:cursor-default"
                          type="checkbox"
                          checked={
                            annotations[currentFrameNumber]?.[part]
                              ?.not_visible || false
                          }
                          disabled={isDone(part)}
                          onChange={() => toggleNotVisible(part)}
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
};

export default CheckList;
