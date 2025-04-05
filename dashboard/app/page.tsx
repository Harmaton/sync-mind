import Features from "@/components/landing-page/features";
import Footer from "@/components/landing-page/footer";
import HeroGeometric from "@/components/landing-page/hero";
import ProblemSolutionCards from "@/components/landing-page/problem";

export default function Home() {
  return (
      <main className="flex flex-col row-start-2 items-center">
        <HeroGeometric />
        <ProblemSolutionCards />
        <Features />
        <Footer />
       </main>
  );
}
