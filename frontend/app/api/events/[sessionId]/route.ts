import { NextRequest } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  const { sessionId } = params;

  // Check if backend SSE endpoint exists
  const backendUrl = `${API_URL}/api/events/${sessionId}`;

  try {
    // Try to connect to backend SSE endpoint
    const response = await fetch(backendUrl, {
      headers: {
        Accept: "text/event-stream",
      },
    });

    if (!response.ok) {
      // If backend doesn't have SSE endpoint, return a basic SSE stream
      // that can be enhanced with Supabase real-time later
      return new Response(
        `data: ${JSON.stringify({
          event_id: "connection",
          session_id: sessionId,
          timestamp: new Date().toISOString(),
          type: "session_stream_started",
          payload: {
            message: "SSE connection established. Backend endpoint not available.",
          },
        })}\n\n`,
        {
          headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            Connection: "keep-alive",
            "Access-Control-Allow-Origin": "*",
          },
        }
      );
    }

    // Proxy the backend SSE stream
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    const stream = new ReadableStream({
      async start(controller) {
        if (!reader) {
          controller.close();
          return;
        }

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            controller.enqueue(new TextEncoder().encode(chunk));
          }
        } catch (error) {
          console.error("SSE proxy error:", error);
          controller.error(error);
        } finally {
          controller.close();
        }
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (error) {
    console.error("Failed to connect to backend SSE:", error);
    // Return a basic SSE stream indicating connection issue
    return new Response(
      `data: ${JSON.stringify({
        event_id: "error",
        session_id: sessionId,
        timestamp: new Date().toISOString(),
        type: "run_error",
        payload: {
          error_type: "connection_error",
          message: "Failed to connect to backend event stream",
          agent: "system",
        },
      })}\n\n`,
      {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
        },
      }
    );
  }
}

