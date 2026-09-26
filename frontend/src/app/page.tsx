import { HeroSection } from "@/components/home/HeroSection";
import { MatchStrip } from "@/components/home/MatchStrip";
import { TeamsAndValues } from "@/components/home/TeamsAndValues";
import { CtaBand } from "@/components/home/CtaBand";

export default function HomePage() {
  return (
    <>
      <HeroSection />
      <MatchStrip />
      <TeamsAndValues />
      <CtaBand />
    </>
  );
}
