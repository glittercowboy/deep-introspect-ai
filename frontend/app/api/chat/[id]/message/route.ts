import { NextRequest, NextResponse } from "next/server";
import { createRouteHandlerClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";

export async function POST(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const supabase = createRouteHandlerClient({ cookies });
    const conversationId = params.id;
    
    // Check authentication
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError || !session) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }
    
    // Check if conversation exists and belongs to user
    const { data: conversation, error: conversationError } = await supabase
      .from("conversations")
      .select("*")
      .eq("id", conversationId)
      .single();
    
    if (conversationError || !conversation) {
      return NextResponse.json(
        { error: "Conversation not found" },
        { status: 404 }
      );
    }
    
    if (conversation.user_id !== session.user.id) {
      return NextResponse.json(
        { error: "Unauthorized to access this conversation" },
        { status: 403 }
      );
    }
    
    // Get request body
    const { content, model = "anthropic" } = await req.json();
    
    if (!content || typeof content !== "string" || content.trim() === "") {
      return NextResponse.json(
        { error: "Message content is required" },
        { status: 400 }
      );
    }
    
    // Store user message
    const { data: userMessage, error: userMessageError } = await supabase
      .from("messages")
      .insert([
        {
          conversation_id: conversationId,
          role: "user",
          content,
          created_at: new Date().toISOString(),
        }
      ])
      .select("*")
      .single();
    
    if (userMessageError) {
      console.error("Error storing user message:", userMessageError);
      return NextResponse.json(
        { error: "Failed to store user message" },
        { status: 500 }
      );
    }
    
    // Update conversation
    await supabase
      .from("conversations")
      .update({
        updated_at: new Date().toISOString(),
        model,
        messages_count: (conversation.messages_count || 0) + 1,
      })
      .eq("id", conversationId);
    
    // Send to backend API for processing (streaming)
    const encoder = new TextEncoder();
    const stream = new TransformStream();
    const writer = stream.writable.getWriter();
    
    // Start background processing
    processMessage(
      conversationId,
      content,
      model,
      writer,
      supabase,
      session.user.id
    ).catch(console.error);
    
    return new NextResponse(stream.readable, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Transfer-Encoding": "chunked",
      },
    });
    
  } catch (error) {
    console.error("Error processing message:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

async function processMessage(
  conversationId: string,
  content: string,
  model: string,
  writer: WritableStreamDefaultWriter<Uint8Array>,
  supabase: any,
  userId: string
) {
  const encoder = new TextEncoder();
  
  try {
    // In a real implementation, this would call your backend API
    // Here we're simulating a streaming response
    
    // Get conversation context
    const { data: messagesData } = await supabase
      .from("messages")
      .select("*")
      .eq("conversation_id", conversationId)
      .order("created_at", { ascending: true });
    
    // Format messages for the API
    const messages = messagesData.map((msg: any) => ({
      role: msg.role,
      content: msg.content,
    }));
    
    // Send to backend API
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const endpoint = model === "anthropic" ? "chat/stream" : "chat/stream";
    
    const response = await fetch(`${apiUrl}/api/v1/${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.API_SECRET_KEY}`,
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        user_id: userId,
        messages,
        model,
      }),
    });
    
    // If the API is not available, simulate a response
    if (!response.ok || !response.body) {
      // Simulate streaming response
      const simulatedResponse = createSimulatedResponse(content);
      
      for (const chunk of simulatedResponse) {
        await writer.write(encoder.encode(chunk));
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      
      // Store the simulated assistant message
      const fullResponse = simulatedResponse.join("");
      await supabase
        .from("messages")
        .insert([
          {
            conversation_id: conversationId,
            role: "assistant",
            content: fullResponse,
            created_at: new Date().toISOString(),
          }
        ]);
      
      // Update conversation count
      await supabase
        .from("conversations")
        .update({
          updated_at: new Date().toISOString(),
          messages_count: (messagesData.length || 0) + 2, // +2 for the user message and assistant response
        })
        .eq("id", conversationId);
      
    } else {
      // Process real streaming response
      const reader = response.body.getReader();
      let assistantMessage = "";
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        const chunk = new TextDecoder().decode(value);
        assistantMessage += chunk;
        
        await writer.write(encoder.encode(chunk));
      }
      
      // Store the complete assistant message
      await supabase
        .from("messages")
        .insert([
          {
            conversation_id: conversationId,
            role: "assistant",
            content: assistantMessage,
            created_at: new Date().toISOString(),
          }
        ]);
      
      // Update conversation count
      await supabase
        .from("conversations")
        .update({
          updated_at: new Date().toISOString(),
          messages_count: (messagesData.length || 0) + 2, // +2 for the user message and assistant response
        })
        .eq("id", conversationId);
    }
    
  } catch (error) {
    console.error("Error processing message:", error);
    await writer.write(encoder.encode("An error occurred while processing your message."));
  } finally {
    await writer.close();
  }
}

// Simulate AI response for development and testing
function createSimulatedResponse(userMessage: string): string[] {
  // Get current date/time
  const now = new Date();
  const timeString = now.toLocaleTimeString();
  const dateString = now.toLocaleDateString();
  
  // Analyze message to generate relevant response
  let responseText = "";
  
  if (userMessage.toLowerCase().includes("hello") || userMessage.toLowerCase().includes("hi")) {
    responseText = "Hello! I'm DeepIntrospect AI, designed to help you better understand yourself through thoughtful conversation. How are you feeling today?";
  } else if (userMessage.toLowerCase().includes("how are you")) {
    responseText = "I'm functioning well, thank you for asking. More importantly, I'm curious about how you're doing today. What's on your mind?";
  } else if (userMessage.toLowerCase().includes("time") || userMessage.toLowerCase().includes("date")) {
    responseText = `It's currently ${timeString} on ${dateString}. How does the passage of time affect your thoughts or feelings today?`;
  } else if (userMessage.toLowerCase().includes("help") || userMessage.toLowerCase().includes("purpose")) {
    responseText = "I'm here to facilitate meaningful self-reflection through our conversations. By discussing your thoughts, experiences, and feelings, I can help you identify patterns and gain insights about yourself. What aspect of yourself would you like to explore today?";
  } else if (userMessage.length < 20) {
    responseText = "I'd love to dive deeper into that. Could you elaborate a bit more? The more you share, the better I can assist with your self-reflection journey.";
  } else {
    responseText = "Thank you for sharing that. It sounds like this is something meaningful to you. I'm curious about how these experiences have shaped your perspective. Could you tell me more about how this relates to your values or goals?";
  }
  
  // Break response into chunks to simulate streaming
  const words = responseText.split(" ");
  const chunks = [];
  let currentChunk = "";
  
  for (const word of words) {
    currentChunk += word + " ";
    
    if (currentChunk.length > 10 || word === words[words.length - 1]) {
      chunks.push(currentChunk);
      currentChunk = "";
    }
  }
  
  return chunks;
}
