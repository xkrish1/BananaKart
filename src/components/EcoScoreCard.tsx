import { Card } from "@/components/ui/card";
import { Leaf } from "lucide-react";

interface EcoScoreCardProps {
  score?: number;
}

const EcoScoreCard = ({ score = 78 }: EcoScoreCardProps) => {
  const getColor = (score: number) => {
    if (score >= 70) return "text-primary";
    if (score >= 40) return "text-warning";
    return "text-destructive";
  };

  const getStrokeColor = (score: number) => {
    if (score >= 70) return "hsl(var(--primary))";
    if (score >= 40) return "hsl(var(--warning))";
    return "hsl(var(--destructive))";
  };

  const circumference = 2 * Math.PI * 70;
  const offset = circumference - (score / 100) * circumference;

  return (
    <Card className="p-6 hover:shadow-lg transition-shadow animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">Eco Score</h3>
        <Leaf className="h-5 w-5 text-primary" />
      </div>
      
      <div className="flex items-center justify-center">
        <div className="relative">
          <svg width="160" height="160" className="transform -rotate-90">
            <circle
              cx="80"
              cy="80"
              r="70"
              fill="none"
              stroke="hsl(var(--muted))"
              strokeWidth="12"
            />
            <circle
              cx="80"
              cy="80"
              r="70"
              fill="none"
              stroke={getStrokeColor(score)}
              strokeWidth="12"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-4xl font-bold ${getColor(score)}`}>{score}</span>
            <span className="text-xs text-muted-foreground">out of 100</span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default EcoScoreCard;
