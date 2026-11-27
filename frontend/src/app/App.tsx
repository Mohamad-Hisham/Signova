import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import HomePage from "../features/home/HomePage";

const AlphabetTranslatorPage = lazy(
  () => import("../features/recognition/pages/AlphabetTranslatorPage"),
);
const WordTranslatorPage = lazy(
  () => import("../features/recognition/pages/WordTranslatorPage"),
);

export default function App() {
  const [path, setPath] = useState(window.location.pathname);

  const navigate = useCallback((nextPath: string) => {
    if (window.location.pathname !== nextPath) {
      window.history.pushState({}, "", nextPath);
    }
    setPath(nextPath);
    window.scrollTo({ top: 0, behavior: "instant" });
  }, []);

  useEffect(() => {
    const handlePopState = () => setPath(window.location.pathname);
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  if (path === "/translator/words") {
    return (
      <Suspense fallback={<div className="route-loading" role="status">Loading translator…</div>}>
        <WordTranslatorPage onHome={() => navigate("/")} />
      </Suspense>
    );
  }
  if (path === "/translator/alphabet") {
    return (
      <Suspense fallback={<div className="route-loading" role="status">Loading translator…</div>}>
        <AlphabetTranslatorPage onHome={() => navigate("/")} />
      </Suspense>
    );
  }
  return (
    <HomePage
      onOpenMode={mode =>
        navigate(mode === "word" ? "/translator/words" : "/translator/alphabet")
      }
    />
  );
}
