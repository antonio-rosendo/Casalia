import { Navbar } from "./components/sections/Navbar";
import { Hero } from "./components/sections/Hero";
import { Forecasts } from "./components/sections/Forecasts";
import { Results } from "./components/sections/Results";
import { Method } from "./components/sections/Method";
import { Footer } from "./components/sections/Footer";

function App() {
  return (
    <div className="min-h-screen bg-neo-white text-neo-black font-sans selection:bg-neo-yellow selection:text-neo-black">
      <Navbar />
      <main>
        <Hero />
        <Forecasts />
        <Results />
        <Method />
      </main>
      <Footer />
    </div>
  );
}

export default App;
