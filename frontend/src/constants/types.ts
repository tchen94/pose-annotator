export interface BodyPartAnnotations {
  [bodyPart: string]: {
    x: number | null;
    y: number | null;
    not_visible: boolean;
  };
}
