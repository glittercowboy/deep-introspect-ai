"use client";

import { useState } from "react";
import Link from "next/link";
import { SparklesCore } from "@/components/ui/aceternity/sparkles";
import MainNav from "@/components/layout/main-nav";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { ChevronRight, Book, Brain, MessageCircle, FileText, Coffee, Pencil, Clock, ThumbsUp } from "lucide-react";

export default function GuidePage() {
  const [activeTab, setActiveTab] = useState("getting-started");

  return (
    <div className="relative min-h-screen pb-12">
      <div className="absolute inset-0 -z-10">
        <SparklesCore
          id="tsparticlesfullpage"
          background="transparent"
          minSize={0.6}
          maxSize={1.4}
          particleDensity={30}
          className="w-full h-full"
          particleColor="#FFFFFF"
        />
      </div>
      
      <MainNav />
      
      <div className="container max-w-7xl px-4 mx-auto mt-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Self-Reflection Guide</h1>
          <p className="text-muted-foreground mt-1">
            Learn how to make the most of DeepIntrospect AI for meaningful self-discovery
          </p>
        </header>
        
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          {/* Sidebar */}
          <div className="md:col-span-3">
            <Card className="sticky top-24">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">Contents</CardTitle>
              </CardHeader>
              <CardContent>
                <nav className="flex flex-col space-y-1">
                  <Button 
                    variant={activeTab === "getting-started" ? "secondary" : "ghost"} 
                    className="justify-start font-normal"
                    onClick={() => setActiveTab("getting-started")}
                  >
                    <Book className="mr-2 h-4 w-4" />
                    Getting Started
                  </Button>
                  <Button 
                    variant={activeTab === "reflection-techniques" ? "secondary" : "ghost"} 
                    className="justify-start font-normal"
                    onClick={() => setActiveTab("reflection-techniques")}
                  >
                    <Brain className="mr-2 h-4 w-4" />
                    Reflection Techniques
                  </Button>
                  <Button 
                    variant={activeTab === "conversation-tips" ? "secondary" : "ghost"} 
                    className="justify-start font-normal"
                    onClick={() => setActiveTab("conversation-tips")}
                  >
                    <MessageCircle className="mr-2 h-4 w-4" />
                    Conversation Tips
                  </Button>
                  <Button 
                    variant={activeTab === "understanding-insights" ? "secondary" : "ghost"} 
                    className="justify-start font-normal"
                    onClick={() => setActiveTab("understanding-insights")}
                  >
                    <FileText className="mr-2 h-4 w-4" />
                    Understanding Insights
                  </Button>
                  <Button 
                    variant={activeTab === "best-practices" ? "secondary" : "ghost"} 
                    className="justify-start font-normal"
                    onClick={() => setActiveTab("best-practices")}
                  >
                    <ThumbsUp className="mr-2 h-4 w-4" />
                    Best Practices
                  </Button>
                </nav>
              </CardContent>
            </Card>
          </div>
          
          {/* Content */}
          <div className="md:col-span-9">
            <Card className="mb-8">
              <CardContent className="pt-6">
                {activeTab === "getting-started" && (
                  <div className="prose dark:prose-invert max-w-none">
                    <h2 className="text-2xl font-bold mb-4">Getting Started with DeepIntrospect AI</h2>
                    
                    <p>
                      Welcome to DeepIntrospect AI, your personal guide for meaningful self-reflection
                      and introspection. Our AI is designed to help you explore your thoughts, beliefs,
                      patterns, and perspectives through natural conversation.
                    </p>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">How It Works</h3>
                    
                    <p>
                      DeepIntrospect AI uses advanced AI technology to engage you in thoughtful
                      conversations that encourage reflection. As you chat, our system:
                    </p>
                    
                    <ul className="list-disc pl-6 mt-2 mb-4">
                      <li>Creates a personalized knowledge graph of your beliefs, values, and patterns</li>
                      <li>Generates insights based on patterns in your conversations</li>
                      <li>Maintains context across multiple sessions</li>
                      <li>Adapts to your communication style and preferences</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">Your First Conversation</h3>
                    
                    <p>
                      Starting your journey is simple:
                    </p>
                    
                    <ol className="list-decimal pl-6 mt-2 mb-4">
                      <li>Click on the "Chat" option in the navigation</li>
                      <li>Start a new conversation with any greeting or question</li>
                      <li>Respond openly and honestly to DeepIntrospect AI's questions</li>
                      <li>Take your time to reflect before responding</li>
                    </ol>
                    
                    <div className="bg-primary/10 p-4 rounded-md my-6 flex items-start">
                      <Coffee className="h-6 w-6 mr-3 mt-1 flex-shrink-0 text-primary" />
                      <div>
                        <h4 className="font-semibold mb-1">Tip: Create a Reflection Routine</h4>
                        <p className="text-sm">
                          Many users find it helpful to set aside 10-15 minutes each day for reflection.
                          A regular practice helps build deeper insights over time.
                        </p>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">What to Expect</h3>
                    
                    <p>
                      In your first few conversations, DeepIntrospect AI will ask questions to understand
                      your baseline thoughts and perspectives. Over time, it will begin to identify patterns
                      and offer more personalized insights.
                    </p>
                    
                    <p>
                      Remember that self-reflection is a journey. The most valuable insights often come
                      after several conversations when the AI has had time to learn your patterns.
                    </p>
                    
                    <div className="mt-6">
                      <Button asChild>
                        <Link href="/chat">Start Your First Conversation</Link>
                      </Button>
                    </div>
                  </div>
                )}
                
                {activeTab === "reflection-techniques" && (
                  <div className="prose dark:prose-invert max-w-none">
                    <h2 className="text-2xl font-bold mb-4">Effective Self-Reflection Techniques</h2>
                    
                    <p>
                      Self-reflection is both an art and a science. These proven techniques will help
                      you get the most out of your conversations with DeepIntrospect AI.
                    </p>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">1. The Five Whys</h3>
                    
                    <p>
                      This technique involves asking "why" recursively to dig deeper into your motivations
                      or beliefs. When DeepIntrospect AI asks you about a belief or preference, try to 
                      question yourself by asking "why" at least five times.
                    </p>
                    
                    <div className="bg-muted p-4 rounded-md my-4">
                      <p className="text-sm italic mb-2">Example:</p>
                      <ul className="list-none pl-0 space-y-2">
                        <li><strong>Statement:</strong> "I feel anxious about public speaking."</li>
                        <li><strong>Why #1:</strong> "Because I'm afraid of being judged."</li>
                        <li><strong>Why #2:</strong> "Because I think others will find flaws in my ideas."</li>
                        <li><strong>Why #3:</strong> "Because I'm not fully confident in my expertise."</li>
                        <li><strong>Why #4:</strong> "Because I compare myself to more experienced speakers."</li>
                        <li><strong>Why #5:</strong> "Because I value external validation too highly."</li>
                      </ul>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">2. Counterfactual Thinking</h3>
                    
                    <p>
                      Challenge your assumptions by considering the opposite. When discussing a belief
                      with DeepIntrospect AI, take a moment to imagine what it would mean if the opposite
                      were true.
                    </p>
                    
                    <div className="bg-muted p-4 rounded-md my-4">
                      <p className="text-sm italic mb-2">Example:</p>
                      <p>"I believe career success requires sacrificing personal life."</p>
                      <p><strong>Counterfactual:</strong> "What if greater personal fulfillment actually leads to more career success?"</p>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">3. Perspective Shifting</h3>
                    
                    <p>
                      When discussing a decision or conflict, try to view it from multiple perspectives.
                      This technique helps develop empathy and uncover blind spots in your thinking.
                    </p>
                    
                    <ul className="list-disc pl-6 mt-2 mb-4">
                      <li>How would a close friend see this situation?</li>
                      <li>What would someone with the opposite values think?</li>
                      <li>How might you view this 10 years from now?</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">4. Journaling Alongside Conversations</h3>
                    
                    <div className="bg-primary/10 p-4 rounded-md my-4 flex items-start">
                      <Pencil className="h-6 w-6 mr-3 mt-1 flex-shrink-0 text-primary" />
                      <div>
                        <h4 className="font-semibold mb-1">Reflection Exercise</h4>
                        <p className="text-sm">
                          Keep a journal alongside your DeepIntrospect AI conversations. After each session,
                          write down the key insights or questions that resonated with you. Review these notes
                          periodically to track your growth.
                        </p>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">5. The Empty Chair Technique</h3>
                    
                    <p>
                      Borrowed from Gestalt therapy, this technique involves imagining a conversation
                      with another person (or even another part of yourself). Share this conversation
                      with DeepIntrospect AI to gain insights into your relationships and inner conflicts.
                    </p>
                    
                    <p>
                      These techniques are most effective when practiced regularly. DeepIntrospect AI can
                      help guide you through these exercises, but the most valuable insights will come
                      from your own sincere reflection.
                    </p>
                  </div>
                )}
                
                {activeTab === "conversation-tips" && (
                  <div className="prose dark:prose-invert max-w-none">
                    <h2 className="text-2xl font-bold mb-4">Having Meaningful Conversations</h2>
                    
                    <p>
                      The quality of insights you receive depends largely on how you engage with
                      DeepIntrospect AI. Here are some tips to make your conversations more productive.
                    </p>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">Be Specific and Concrete</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
                      <div className="bg-destructive/10 p-4 rounded-md">
                        <p className="font-semibold mb-2">Less Effective</p>
                        <p className="text-sm">"I've been feeling bad lately."</p>
                      </div>
                      <div className="bg-green-500/10 p-4 rounded-md">
                        <p className="font-semibold mb-2">More Effective</p>
                        <p className="text-sm">"I've been feeling anxious before team meetings at work for the past two weeks."</p>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">Embrace Vulnerability</h3>
                    
                    <p>
                      The most meaningful insights often come from exploring uncomfortable topics or
                      acknowledging uncertainties. DeepIntrospect AI creates a safe space for this exploration.
                    </p>
                    
                    <div className="bg-primary/10 p-4 rounded-md my-6">
                      <p className="text-sm">
                        "I realize I might be contributing to the conflict with my colleague, but I'm not sure how."
                      </p>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">Ask for Specific Types of Questions</h3>
                    
                    <p>
                      You can guide the conversation by asking DeepIntrospect AI to focus on particular areas:
                    </p>
                    
                    <ul className="list-disc pl-6 mt-2 mb-4">
                      <li>"Can you ask me questions about my work-life balance?"</li>
                      <li>"I'd like to explore my communication patterns in relationships."</li>
                      <li>"Help me reflect on how I handle stress."</li>
                    </ul>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">Challenge the AI's Assumptions</h3>
                    
                    <p>
                      If DeepIntrospect AI makes an observation that doesn't resonate with you, don't 
                      hesitate to push back. This dialogue helps refine the AI's understanding of you.
                    </p>
                    
                    <div className="bg-muted p-4 rounded-md my-4">
                      <p className="text-sm italic mb-2">Example:</p>
                      <p><strong>AI:</strong> "It seems like you value stability over growth in your career."</p>
                      <p><strong>You:</strong> "That's interesting, but I don't think that's accurate. I value growth but in a sustainable way. Let me explain..."</p>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">Take Time to Reflect</h3>
                    
                    <div className="bg-primary/10 p-4 rounded-md my-4 flex items-start">
                      <Clock className="h-6 w-6 mr-3 mt-1 flex-shrink-0 text-primary" />
                      <div>
                        <h4 className="font-semibold mb-1">Thoughtful Pauses</h4>
                        <p className="text-sm">
                          Don't feel pressured to respond immediately. Take time to reflect on the AI's
                          questions or observations before responding. The conversation will wait for you.
                        </p>
                      </div>
                    </div>
                    
                    <p>
                      Remember that meaningful self-reflection is a process, not a destination. Be patient
                      with yourself as you explore and grow.
                    </p>
                  </div>
                )}
                
                {activeTab === "understanding-insights" && (
                  <div className="prose dark:prose-invert max-w-none">
                    <h2 className="text-2xl font-bold mb-4">Understanding Your Insights</h2>
                    
                    <p>
                      As you continue to use DeepIntrospect AI, the system will generate insights about your
                      patterns, beliefs, values, and more. Here's how to interpret and use these insights effectively.
                    </p>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">Types of Insights</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-6">
                      <div className="bg-blue-500/10 p-4 rounded-md">
                        <h4 className="font-semibold mb-2">Beliefs</h4>
                        <p className="text-sm">
                          Your underlying assumptions about how the world works. These shape your decisions and interpretations.
                        </p>
                      </div>
                      <div className="bg-purple-500/10 p-4 rounded-md">
                        <h4 className="font-semibold mb-2">Values</h4>
                        <p className="text-sm">
                          What you consider important or worthwhile. These guide your priorities and evaluations.
                        </p>
                      </div>
                      <div className="bg-amber-500/10 p-4 rounded-md">
                        <h4 className="font-semibold mb-2">Patterns</h4>
                        <p className="text-sm">
                          Recurring approaches to situations or relationships. These can be both helpful and limiting.
                        </p>
                      </div>
                      <div className="bg-emerald-500/10 p-4 rounded-md">
                        <h4 className="font-semibold mb-2">Traits</h4>
                        <p className="text-sm">
                          Your characteristic ways of thinking, feeling, and behaving across situations.
                        </p>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">How to Use the Insights Dashboard</h3>
                    
                    <p>
                      The Insights page provides multiple ways to explore your personal data:
                    </p>
                    
                    <ul className="list-disc pl-6 mt-2 mb-4">
                      <li><strong>List View:</strong> Shows all insights chronologically with filtering options</li>
                      <li><strong>Graph View:</strong> Visualizes connections between different insights</li>
                      <li><strong>Summary View:</strong> Provides a narrative overview of key patterns</li>
                    </ul>
                    
                    <div className="bg-primary/10 p-4 rounded-md my-6 flex items-start">
                      <Brain className="h-6 w-6 mr-3 mt-1 flex-shrink-0 text-primary" />
                      <div>
                        <h4 className="font-semibold mb-1">Connecting the Dots</h4>
                        <p className="text-sm">
                          Pay special attention to insights that appear in multiple conversations or connect
                          to multiple areas of your life. These often represent core patterns.
                        </p>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">Evaluating Insights</h3>
                    
                    <p>
                      Not all insights will feel equally accurate or helpful. When reviewing your insights, consider:
                    </p>
                    
                    <ul className="list-disc pl-6 mt-2 mb-4">
                      <li><strong>Resonance:</strong> Does this insight feel true to your experience?</li>
                      <li><strong>Usefulness:</strong> Does this insight help you understand yourself better?</li>
                      <li><strong>Actionability:</strong> Can you use this insight to make changes in your life?</li>
                    </ul>
                    
                    <p>
                      Remember that insights are hypotheses, not final judgments. Use them as starting points
                      for deeper reflection rather than fixed conclusions about yourself.
                    </p>
                    
                    <div className="mt-6">
                      <Button asChild>
                        <Link href="/insights">Explore Your Insights</Link>
                      </Button>
                    </div>
                  </div>
                )}
                
                {activeTab === "best-practices" && (
                  <div className="prose dark:prose-invert max-w-none">
                    <h2 className="text-2xl font-bold mb-4">Best Practices for Growth</h2>
                    
                    <p>
                      To make the most of DeepIntrospect AI and support your personal growth journey,
                      consider these best practices from users who have experienced significant insights.
                    </p>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">1. Create a Regular Reflection Routine</h3>
                    
                    <p>
                      Consistency is key to deeper self-understanding. Set aside 15-30 minutes at least
                      twice a week for reflection conversations.
                    </p>
                    
                    <div className="bg-primary/10 p-4 rounded-md my-4 flex items-start">
                      <Coffee className="h-6 w-6 mr-3 mt-1 flex-shrink-0 text-primary" />
                      <div>
                        <h4 className="font-semibold mb-1">User Tip</h4>
                        <p className="text-sm">
                          "I have my reflection sessions on Tuesday and Friday mornings with a cup of tea.
                          The routine itself signals to my brain that it's time to be introspective."
                        </p>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">2. Alternate Between Different Topics</h3>
                    
                    <p>
                      While it's valuable to explore issues in depth, alternating between different life
                      areas helps build a more comprehensive understanding of your patterns.
                    </p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
                      <div className="bg-muted p-4 rounded-md">
                        <p className="font-semibold mb-2">Topic Areas to Explore</p>
                        <ul className="list-disc pl-4 text-sm space-y-1">
                          <li>Work and career perspectives</li>
                          <li>Relationship patterns</li>
                          <li>Health and well-being approaches</li>
                          <li>Values and life purpose</li>
                          <li>Creative expression</li>
                        </ul>
                      </div>
                      <div className="bg-muted p-4 rounded-md">
                        <p className="font-semibold mb-2">Reflection Questions</p>
                        <ul className="list-disc pl-4 text-sm space-y-1">
                          <li>What energizes you in this area?</li>
                          <li>What patterns keep repeating?</li>
                          <li>What beliefs influence your approach?</li>
                          <li>What would you like to change?</li>
                          <li>How does this area connect to others?</li>
                        </ul>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">3. Revisit Past Conversations</h3>
                    
                    <p>
                      Your perspective changes over time. Regularly revisit past conversations and insights
                      to notice how your understanding has evolved.
                    </p>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">4. Connect Insights to Actions</h3>
                    
                    <p>
                      Self-reflection is most valuable when it leads to positive changes. For key insights,
                      consider what small, specific actions you might take in response.
                    </p>
                    
                    <div className="bg-muted p-4 rounded-md my-4">
                      <p className="text-sm italic mb-2">Example:</p>
                      <p><strong>Insight:</strong> "I tend to avoid difficult conversations until problems escalate."</p>
                      <p><strong>Action:</strong> "I'll practice addressing one small issue this week when it first arises."</p>
                    </div>
                    
                    <h3 className="text-xl font-semibold mt-6 mb-3">5. Combine with Other Growth Practices</h3>
                    
                    <p>
                      DeepIntrospect AI works well alongside other personal growth practices like:
                    </p>
                    
                    <ul className="list-disc pl-6 mt-2 mb-4">
                      <li>Journaling or creative writing</li>
                      <li>Meditation or mindfulness practices</li>
                      <li>Physical exercise</li>
                      <li>Reading in areas of personal interest</li>
                      <li>Conversations with trusted friends</li>
                    </ul>
                    
                    <p>
                      Remember that self-reflection is not about achieving perfection, but about growing
                      in self-awareness and making intentional choices aligned with your values.
                    </p>
                    
                    <div className="mt-6">
                      <Button asChild>
                        <Link href="/chat">Start Your Journey</Link>
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
