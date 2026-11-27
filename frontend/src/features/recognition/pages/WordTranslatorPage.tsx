import RecognitionWorkspace from "../RecognitionWorkspace";

type Props = { onHome: () => void };

export default function WordTranslatorPage({ onHome }: Props) {
  return <RecognitionWorkspace mode="word" onHome={onHome} />;
}
