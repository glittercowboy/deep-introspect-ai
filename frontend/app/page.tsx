import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { SparklesCore } from '@/components/ui/aceternity/sparkles';

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-6 relative overflow-hidden">
      <div className="absolute inset-0 w-full h-full">
        <SparklesCore
          id="tsparticlesfullpage"
          background="transparent"
          minSize={0.6}
          maxSize={1.4}
          particleDensity={50}
          className="w-full h-full"
          particleColor="#FFFFFF"
        />
      </div>
      
      <div className="container max-w-6xl relative z-10">
        <div className="flex flex-col items-center text-center space-y-6">
          <h1 className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            DeepIntrospect AI
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-200 max-w-3xl">
            A groundbreaking self-reflection chatbot that helps you understand yourself and your life patterns through AI-assisted introspection.
          </p>
          
          <div className="flex flex-col md:flex-row gap-4 mt-8">
            <Button asChild size="lg" className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700">
              <Link href="/chat">
                Start Conversation
              </Link>
            </Button>
            
            <Button asChild size="lg" variant="outline" className="border-gray-500 hover:bg-gray-800">
              <Link href="/insights">
                View Insights
              </Link>
            </Button>
          </div>
          
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard 
              title="Deep Learning Profile" 
              description="Creates a comprehensive understanding of you through natural conversation"
              icon="🧠"
            />
            <FeatureCard 
              title="Knowledge Graph" 
              description="Builds connections between your information to discover patterns"
              icon="🔄"
            />
            <FeatureCard 
              title="Persistent Memory" 
              description="Conversations and insights are saved for continuous learning"
              icon="💾"
            />
          </div>
        </div>
      </div>
    </main>
  );
}

function FeatureCard({ title, description, icon }: { title: string, description: string, icon: string }) {
  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition-all">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-300">{description}</p>
    </div>
  );
}