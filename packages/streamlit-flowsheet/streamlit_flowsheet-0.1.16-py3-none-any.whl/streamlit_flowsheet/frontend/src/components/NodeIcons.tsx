import React from 'react';
import { loadIcon, createIconComponent, IconProps } from '../utils/iconLoader';

export const DefaultNodeIcon: React.FC<IconProps> = ({ size = 40, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="20" r="8" stroke={color} strokeWidth="2" fill={color} fillOpacity="0.2"/>
    <path d="M20 12 L20 5" stroke={color} strokeWidth="2"/>
    <path d="M20 28 L20 35" stroke={color} strokeWidth="2"/>
    <path d="M12 20 L5 20" stroke={color} strokeWidth="2"/>
    <path d="M28 20 L35 20" stroke={color} strokeWidth="2"/>
  </svg>
);

export const WellNodeIcon: React.FC<IconProps> = ({ size = 40, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 5 L20 35" stroke={color} strokeWidth="2"/>
    <path d="M15 10 L20 5 L25 10" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <rect x="16" y="25" width="8" height="10" fill={color}/>
    <path d="M10 20 L30 20" stroke={color} strokeWidth="1"/>
  </svg>
);

export const ReservoirNodeIcon: React.FC<IconProps> = ({ size = 40, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="5" y="10" width="30" height="20" rx="4" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M5 15 L35 15" stroke={color} strokeWidth="1" strokeDasharray="2 2"/>
    <circle cx="20" cy="22" r="2" fill={color}/>
  </svg>
);

export const InletNodeIcon: React.FC<IconProps> = ({ size = 40, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="10" width="20" height="20" rx="2" stroke={color} strokeWidth="2" fill="none"/>
    <path d="M15 20 L25 20 M20 15 L20 25" stroke={color} strokeWidth="2" strokeLinecap="round"/>
    <path d="M30 20 L35 20" stroke={color} strokeWidth="2"/>
    <path d="M33 17 L35 20 L33 23" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

export const getNodeIcon = (type: string) => {
  const typeLower = type.toLowerCase();

  switch (typeLower) {
    case 'tank':
    case 'reservoir':
      return ReservoirNodeIcon;
    case 'well':
      return WellNodeIcon;
    case 'sep':
    case 'separator':
    case 'gas-liquid separator':
    case 'vessel':
      const vesselSvgUrl = loadIcon('vessel-v1');
      if (vesselSvgUrl) {
        return createIconComponent(vesselSvgUrl, 1.2);
      }
      return DefaultNodeIcon;
    case 'joint':
      return DefaultNodeIcon;
    case 'pipe':
      const pipeSvgUrl = loadIcon('pipe-v1');
      if (pipeSvgUrl) {
        return createIconComponent(pipeSvgUrl);
      }
      return DefaultNodeIcon;
    case 'inlgen':
    case 'inlet':
    case 'inlet_generator':
      return InletNodeIcon;
    case 'pump':
      const pumpSvgUrl = loadIcon('pump-v1');
      if (pumpSvgUrl) {
        return createIconComponent(pumpSvgUrl);
      }
      return DefaultNodeIcon;
    case 'reactor':
      const reactorSvgUrl = loadIcon('batch-reactor-v1');
      if (reactorSvgUrl) {
        return createIconComponent(reactorSvgUrl);
      }
      return DefaultNodeIcon;
    case 'compressor':
      const compressorSvgUrl = loadIcon('compressor-v1');
      if (compressorSvgUrl) {
        return createIconComponent(compressorSvgUrl);
      }
      return DefaultNodeIcon;
    case 'fired-heater':
    case 'furnace':
    case 'heater':
      const firedHeaterSvgUrl = loadIcon('fired-heater-v1');
      if (firedHeaterSvgUrl) {
        return createIconComponent(firedHeaterSvgUrl);
      }
      return DefaultNodeIcon;
    case 'heat-exchanger':
    case 'heat exchanger':
      const heatExchangerSvgUrl = loadIcon('heat-exchanger-v1');
      if (heatExchangerSvgUrl) {
        return createIconComponent(heatExchangerSvgUrl);
      }
      return DefaultNodeIcon;
    case 'turbine':
      const turbineSvgUrl = loadIcon('turbine-v1');
      if (turbineSvgUrl) {
        return createIconComponent(turbineSvgUrl);
      }
      return DefaultNodeIcon;
    case 'valve':
      const valveSvgUrl = loadIcon('valve-v1');
      if (valveSvgUrl) {
        return createIconComponent(valveSvgUrl);
      }
      return DefaultNodeIcon;
    case 'material-stream':
    case 'material stream':
      const materialStreamSvgUrl = loadIcon('material-stream-v1');
      if (materialStreamSvgUrl) {
        return createIconComponent(materialStreamSvgUrl);
      }
      return DefaultNodeIcon;
    case 'conversion-reactor':
    case 'conversion reactor':
      const conversionReactorSvgUrl = loadIcon('vertical-vessel-v1');
      if (conversionReactorSvgUrl) {
        return createIconComponent(conversionReactorSvgUrl);
      }
      return DefaultNodeIcon;
    case 'energy-stream':
    case 'energy stream':
      const energyStreamSvgUrl = loadIcon('energy-stream-v1');
      if (energyStreamSvgUrl) {
        return createIconComponent(energyStreamSvgUrl);
      }
      return DefaultNodeIcon;
    case 'stream-mixer':
    case 'stream mixer':
      const streamMixerSvgUrl = loadIcon('mixer');
      if (streamMixerSvgUrl) {
        return createIconComponent(streamMixerSvgUrl);
      }
      return DefaultNodeIcon;
    default:
      return DefaultNodeIcon;
  }
};