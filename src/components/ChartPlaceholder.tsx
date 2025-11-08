import { Card } from "@/components/ui/card";
import { BarChart3 } from "lucide-react";

const ChartPlaceholder = () => {
  // Mock data for bars
  const data = [65, 78, 72, 85, 80, 88, 78];
  const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const maxValue = Math.max(...data);

  return (
    <Card className="p-6 hover:shadow-lg transition-shadow animate-slide-up">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-foreground">Eco Score Trend</h3>
        <BarChart3 className="h-5 w-5 text-primary" />
      </div>
      
      <div className="h-64 flex items-end justify-between gap-4">
        {data.map((value, index) => (
          <div key={index} className="flex-1 flex flex-col items-center gap-2">
            <div className="w-full bg-secondary rounded-t-lg relative overflow-hidden" style={{ height: `${(value / maxValue) * 100}%` }}>
              <div 
                className="absolute inset-0 bg-gradient-to-t from-primary to-primary/60 animate-slide-up"
                style={{ animationDelay: `${index * 0.1}s` }}
              />
            </div>
            <span className="text-xs text-muted-foreground">{labels[index]}</span>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-border flex items-center justify-between text-sm">
        <span className="text-muted-foreground">Average</span>
        <span className="font-semibold text-primary">77.1</span>
      </div>
    </Card>
  );
};

export default ChartPlaceholder;
