// Type declarations for Backpack components that may not have proper TypeScript definitions

declare module '@skyscanner/backpack-web/bpk-component-select' {
  import { ComponentType, SelectHTMLAttributes } from 'react';

  interface BpkSelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
    id: string;
    name: string;
    value: string;
    large?: boolean;
    docked?: boolean;
    dockedFirst?: boolean;
    dockedMiddle?: boolean;
    dockedLast?: boolean;
    valid?: boolean;
    image?: React.ReactNode;
  }

  const BpkSelect: ComponentType<BpkSelectProps>;
  export default BpkSelect;
}

declare module '@skyscanner/bpk-foundations-web/base' {
  // This module provides CSS styles, no exports needed
  const styles: void;
  export default styles;
}
