const strHasLength = (str: unknown): str is string => typeof str === 'string' && str.length > 0;

export { strHasLength };
