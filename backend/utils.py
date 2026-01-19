import pandas as pd

def process_annotations(data: dict) -> pd.DataFrame:
    """
    Process annotations dictionary into long-format DataFrame.

    Parameters
    ----------
    data : dict
        Annotations data with frame numbers as keys and keypoint data as
        values. Should also contain 'orig_width', 'orig_height',
        'render_width', and 'render_height'.

    Returns
    -------
    annotations_df : pd.DataFrame
        A long-format DataFrame containing annotations.
    """

    # Extract dimension metadata
    orig_width = data.pop('orig_width')
    orig_height = data.pop('orig_height')
    render_width = data.pop('render_width')
    render_height = data.pop('render_height')

    # Create long-format DataFrame
    records = []
    for frame_num, keypoints in data.items():
        for body_part, ann in keypoints.items():
            keypoint_name = '_'.join(body_part.lower().split(' '))
            records.append({
                'frame_num': int(frame_num),
                'keypoint_name': keypoint_name,
                'x': ann['x'],
                'y': ann['y'],
                'visible': not ann['not_visible']
            })
    annotations_df = pd.DataFrame(records)

    # Add keypoint_id column
    keypoint_mapping = {
        'nose': 0,
        'left_eye': 1,
        'right_eye': 2,
        'left_ear': 3,
        'right_ear': 4,
        'left_shoulder': 5,
        'right_shoulder': 6,
        'left_elbow': 7,
        'right_elbow': 8,
        'left_wrist': 9,
        'right_wrist': 10,
        'left_hip': 11,
        'right_hip': 12,
        'left_knee': 13,
        'right_knee': 14,
        'left_ankle': 15,
        'right_ankle': 16
    }
    annotations_df['keypoint_id'] = annotations_df['keypoint_name'].map(
        keypoint_mapping)

    # Calculate scale factors for coordinate conversion
    scale_x = orig_width / render_width if render_width else 1
    scale_y = orig_height / render_height if render_height else 1

    # Rescale coordinates to original dimensions
    annotations_df['x'] = (annotations_df['x'] * scale_x).apply(
        lambda x: int(x) if pd.notna(x) else None)
    annotations_df['y'] = (annotations_df['y'] * scale_y).apply(
        lambda y: int(y) if pd.notna(y) else None)

    # Sort values and reorder columns
    annotations_df = annotations_df.sort_values(
        ['frame_num', 'keypoint_id']).reset_index(drop = True)
    annotations_df = annotations_df[
        ['frame_num', 'keypoint_id', 'keypoint_name', 'x', 'y', 'visible']]

    return annotations_df