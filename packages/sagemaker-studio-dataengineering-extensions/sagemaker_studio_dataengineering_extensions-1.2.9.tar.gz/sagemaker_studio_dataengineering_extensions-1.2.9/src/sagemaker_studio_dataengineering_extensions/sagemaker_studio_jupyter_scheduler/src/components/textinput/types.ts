enum TextInputSize {
  Large,
  Medium,
  Small,
}

enum TextInputVariant {
  Filled = 'filled',
}

export interface InputStylesProps {
  size: TextInputSize;
}

export { TextInputSize, TextInputVariant };
