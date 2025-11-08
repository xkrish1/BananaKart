import { Card } from "@/components/ui/card";
import { TrendingDown } from "lucide-react";

interface VarianceCardProps {
  variance?: number;
}

const VarianceCard = ({ variance = -8.2 }: VarianceCardProps) => {
  const isPositive = variance < 0;
  
  return (
    <Card className="p-6 hover:shadow-lg transition-shadow animate-fade-in" style={{ animationDelay: "0.2s" }}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">Cost Variance</h3>
        <TrendingDown className={`h-5 w-5 ${isPositive ? "text-primary" : "text-destructive"}`} />
      </div>
      
      <div className="space-y-4">
        <div className="flex items-baseline gap-2">
          <span className={`text-4xl font-bold ${isPositive ? "text-primary" : "text-destructive"}`}>
            {variance}%
          </span>
        </div>
        
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">vs. baseline</span>
            <span className="font-medium text-foreground">$128</span>
          </div>
          
          <div className="relative h-3 bg-secondary rounded-full overflow-hidden">
            <div className="absolute inset-y-0 left-0 bg-primary rounded-full" style={{ width: "40%" }}></div>
            <div className="absolute inset-y-0 left-[40%] bg-destructive rounded-full" style={{ width: "20%" }}></div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default VarianceCard;
