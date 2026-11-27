import RecognitionWorkspace from "../RecognitionWorkspace";

type Props = { onHome: () => void };

export default function AlphabetTranslatorPage({ onHome }: Props) {
  return <RecognitionWorkspace mode="alphabet" onHome={onHome} />;
}
