import React from "react";

export interface IconProps {
  size?: number;
  color?: string;
  className?: string;
}

export type IconComponent = React.FC<IconProps>;

const iconModules = import.meta.glob<string>("../assets/icons/*.svg", {
  as: "url",
  eager: true,
});

const iconCache: Record<string, string> = {};

Object.entries(iconModules).forEach(([path, url]) => {
  const iconName = path.split("/").pop()?.replace(".svg", "") || "";
  iconCache[iconName] = url as string;
});

export const loadIcon = (iconName: string): string | undefined => {
  return iconCache[iconName.toLowerCase()];
};

export const createIconComponent = (
  svgUrl: string,
  scaleFactor: number = 1,
): IconComponent => {
  const IconComponent: IconComponent = (
    { size = 40, color: _color = "currentColor", className },
  ) => {
    // Apply scaling factor to the size
    const scaledSize = size * scaleFactor;

    return React.createElement("img", {
      src: svgUrl,
      width: scaledSize,
      height: scaledSize,
      className: className,
      style: {
        pointerEvents: "none",
      },
      alt: "icon",
    });
  };

  return IconComponent;
};

export const getAvailableIcons = (): string[] => {
  return Object.keys(iconCache);
};
