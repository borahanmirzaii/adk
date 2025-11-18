import { NextRequest } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  const { sessionId } = params;

  if (!sessionId) {
    return new Response(
      `event: run_error\ndata: ${JSON.stringify({
        event_id: "error",
        session_id: "",
        timestamp: new Date().toISOString(),
        type: "run_error",
        payload: {
          error_type: "validation_error",
          message: "session_id is required",
          agent: "system",
        },
      })}\n\n`,
      {
        status: 400,
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
        },
      }
    );
  }

  const backendUrl = `${API_URL}/api/events/${sessionId}`;

  try {
    // Connect to backend SSE endpoint
    const response = await fetch(backendUrl, {
      headers: {
        Accept: "text/event-stream",
        "Cache-Control": "no-cache",
      },
      // @ts-ignore - Next.js fetch doesn't have signal in types but it works
      signal: request.signal,
    });

    if (!response.ok) {
      // Backend endpoint not available - return error event
      return new Response(
        `event: run_error\ndata: ${JSON.stringify({
          event_id: "error",
          session_id: sessionId,
          timestamp: new Date().toISOString(),
          type: "run_error",
          payload: {
            error_type: "backend_unavailable",
            message: `Backend SSE endpoint returned ${response.status}: ${response.statusText}`,
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

    if (!response.body) {
      throw new Error("Response body is null");
    }

    // Create a readable stream that proxies the backend SSE stream
    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body!.getReader();
        const decoder = new TextDecoder();

        try {
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              controller.close();
              break;
            }

            // Decode and forward the chunk
            const chunk = decoder.decode(value, { stream: true });
            controller.enqueue(new TextEncoder().encode(chunk));
          }
        } catch (error) {
          console.error("[SSE Proxy] Error reading stream:", error);
          
          // Send error event before closing
          const errorEvent = `event: run_error\ndata: ${JSON.stringify({
            event_id: "error",
            session_id: sessionId,
            timestamp: new Date().toISOString(),
            type: "run_error",
            payload: {
              error_type: "stream_error",
              message: error instanceof Error ? error.message : "Unknown stream error",
              agent: "system",
            },
          })}\n\n`;
          
          controller.enqueue(new TextEncoder().encode(errorEvent));
          controller.close();
        } finally {
          reader.releaseLock();
        }
      },
      
      cancel() {
        // Clean up when client disconnects
        response.body?.cancel();
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
        "X-Accel-Buffering": "no", // Disable nginx buffering
      },
    });
  } catch (error) {
    console.error("[SSE Proxy] Failed to connect to backend:", error);
    
    // Return error event
    return new Response(
      `event: run_error\ndata: ${JSON.stringify({
        event_id: "error",
        session_id: sessionId,
        timestamp: new Date().toISOString(),
        type: "run_error",
        payload: {
          error_type: "connection_error",
          message: error instanceof Error ? error.message : "Failed to connect to backend event stream",
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

