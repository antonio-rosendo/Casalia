import { Navbar } from "./components/sections/Navbar";
import { Hero } from "./components/sections/Hero";
import { Estimator } from "./components/sections/Estimator";
import { Methodology } from "./components/sections/Methodology";
import { SegmentsFAQ } from "./components/sections/SegmentsFAQ";
import { Footer } from "./components/sections/Footer";

function App() {
  return (
    <div className="min-h-screen bg-neo-white text-neo-black font-sans selection:bg-neo-yellow selection:text-neo-black">
      <Navbar />
      <main>
        <Hero />
        <Estimator />
        <Methodology />
        <SegmentsFAQ />
      </main>
      <Footer />
    </div>
  );
}

export default App;

