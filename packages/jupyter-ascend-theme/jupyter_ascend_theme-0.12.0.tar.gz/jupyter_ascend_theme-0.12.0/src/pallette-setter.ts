export interface IBasePalletteSetter {
  readonly name: string;
  readonly type: 'light' | 'dark';
  setColorPallette: () => void;
}
