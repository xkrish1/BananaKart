import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { Leaf, Send } from "lucide-react";
import Navbar from "@/components/Navbar";

const Analyze = () => {
  const [recipe, setRecipe] = useState("");
  const [urgency, setUrgency] = useState("soon");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!recipe.trim()) {
      toast.error("Please enter a recipe to analyze");
      return;
    }
    
    toast.success("Recipe analyzed successfully!", {
      description: "Check your dashboard for optimization insights.",
    });
    
    // Reset form
    setRecipe("");
    setUrgency("soon");
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold text-foreground">Analyze Your Recipe</h1>
            <p className="text-lg text-muted-foreground">
              Paste your recipe below and let our AI optimize your grocery shopping for sustainability and cost.
            </p>
          </div>
          
          <Card className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label htmlFor="recipe" className="text-sm font-medium text-foreground">
                  Recipe
                </label>
                <Textarea
                  id="recipe"
                  placeholder="Paste your recipe here...&#10;&#10;Example:&#10;- 2 cups of pasta&#10;- 1 cup of tomato sauce&#10;- 1/2 cup parmesan cheese&#10;- Fresh basil"
                  value={recipe}
                  onChange={(e) => setRecipe(e.target.value)}
                  className="min-h-[200px] resize-none"
                />
              </div>
              
              <div className="space-y-2">
                <label htmlFor="urgency" className="text-sm font-medium text-foreground">
                  When do you need these ingredients?
                </label>
                <Select value={urgency} onValueChange={setUrgency}>
                  <SelectTrigger id="urgency">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tonight">Tonight</SelectItem>
                    <SelectItem value="soon">This week</SelectItem>
                    <SelectItem value="later">No rush</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <Button type="submit" size="lg" className="w-full">
                <Leaf className="mr-2 h-5 w-5" />
                Analyze Recipe
                <Send className="ml-2 h-4 w-4" />
              </Button>
            </form>
          </Card>
          
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="p-6 bg-primary/5 border-primary/20">
              <h3 className="font-semibold text-foreground mb-2">What we analyze</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>✓ Ingredient availability</li>
                <li>✓ Seasonal pricing</li>
                <li>✓ Carbon footprint</li>
                <li>✓ Local supplier options</li>
              </ul>
            </Card>
            
            <Card className="p-6 bg-primary/5 border-primary/20">
              <h3 className="font-semibold text-foreground mb-2">You'll receive</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>✓ Optimized shopping list</li>
                <li>✓ Route suggestions</li>
                <li>✓ Cost breakdown</li>
                <li>✓ Sustainability score</li>
              </ul>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analyze;
