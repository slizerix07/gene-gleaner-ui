
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const isUrlEmpty = (url: string): boolean => {
  return url.trim() === "";
};
