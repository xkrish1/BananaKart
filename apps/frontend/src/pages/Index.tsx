import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Leaf, BarChart3, Sparkles } from "lucide-react";
import Navbar from "@/components/Navbar";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center space-y-8 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">AI-Powered Grocery Optimization</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-bold text-foreground leading-tight">
            🍌 Bananakart
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            AI for Sustainable Grocery Optimization
          </p>
          
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Smart recipe analysis, optimal routing, and eco-friendly shopping decisions powered by artificial intelligence.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link to="/analyze">
              <Button size="lg" className="w-full sm:w-auto">
                <Leaf className="mr-2 h-5 w-5" />
                Analyze Recipe
              </Button>
            </Link>
            <Link to="/dashboard">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                <BarChart3 className="mr-2 h-5 w-5" />
                View Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="text-center space-y-4 p-6 rounded-2xl bg-card hover:shadow-lg transition-shadow animate-slide-up">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10">
              <Leaf className="h-6 w-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-foreground">Eco Score</h3>
            <p className="text-muted-foreground">
              Track your environmental impact with real-time sustainability metrics.
            </p>
          </div>
          
          <div className="text-center space-y-4 p-6 rounded-2xl bg-card hover:shadow-lg transition-shadow animate-slide-up" style={{ animationDelay: "0.1s" }}>
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10">
              <BarChart3 className="h-6 w-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-foreground">Smart Analytics</h3>
            <p className="text-muted-foreground">
              Optimize costs and reduce waste with AI-powered insights.
            </p>
          </div>
          
          <div className="text-center space-y-4 p-6 rounded-2xl bg-card hover:shadow-lg transition-shadow animate-slide-up" style={{ animationDelay: "0.2s" }}>
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-foreground">AI Optimization</h3>
            <p className="text-muted-foreground">
              Get personalized recommendations for sustainable shopping.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
