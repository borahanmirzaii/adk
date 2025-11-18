<!-- 4c38b56c-f3c9-443a-835c-b352bbb97f06 4793a77c-4842-4188-87ec-91a37b70e71d -->
# Fix Critical Issues and Improve Codebase

## Overview

This plan addresses all weaknesses identified in the code audit, prioritized by impact and dependencies. Focus on making the system production-ready with proper error handling, memory management, and testing.

## Phase 1: Critical Fixes (Week 1)

### 1.1 Backend SSE Endpoint Implementation

**Priority**: CRITICAL - Blocks all real-time functionality

**Tasks**:

- Create `backend/app/api/routes/events.py` with SSE endpoint
- Register events router in `backend/app/main.py`
- Implement `/api/events/{sessionId}` endpoint using EventBus
- Add proper error handling and connection cleanup
- Test SSE streaming with sample events

**Files to create/modify**:

- `backend/app/api/routes/events.py` (NEW)
- `backend/app/main.py` (MODIFY - add events router)
- `backend/app/dependencies.py` (VERIFY - Redis client exists)

**Acceptance Criteria**:

- SSE endpoint returns proper SSE format
- Events stream correctly from Redis Pub/Sub
- Connection cleanup on client disconnect
- Error handling for invalid sessions

### 1.2 Fix useAgentEvents Hook Dependencies

**Priority**: CRITICAL - Causes memory leaks and stale closures

**Tasks**:

- Fix dependency array in `useAgentEvents.ts`
- Use `useCallback` for handlers to stabilize references
- Add proper cleanup for EventSource
- Prevent multiple connections per session

**Files to modify**:

- `frontend/hooks/useAgentEvents.ts`

**Changes**:

```typescript
// Wrap handlers in useCallback or use useRef
// Add handlers to dependency array properly
// Ensure single EventSource per sessionId
```

### 1.3 Add Event Limits to Prevent Memory Leaks

**Priority**: CRITICAL - Prevents unbounded memory growth

**Tasks**:

- Add MAX_EVENTS constant (1000)
- Implement event limiting in AgentTimeline
- Implement log limiting in LiveConsole
- Add cleanup for old events

**Files to modify**:

- `frontend/components/agents/AgentTimeline.tsx`
- `frontend/components/agents/LiveConsole.tsx`
- `frontend/lib/constants.ts` (NEW - for shared constants)

**Implementation**:

```typescript
const MAX_EVENTS = 1000;
setEvents((prev) => {
  const updated = [...prev, event];
  return updated.slice(-MAX_EVENTS);
});
```

### 1.4 Fix SSE Proxy Endpoint

**Priority**: HIGH - Frontend won't work without this

**Tasks**:

- Update proxy to properly handle backend SSE stream
- Add fallback to Supabase real-time if backend unavailable
- Improve error messages
- Add connection status tracking

**Files to modify**:

- `frontend/app/api/events/[sessionId]/route.ts`

## Phase 2: Integration & Error Handling (Week 2)

### 2.1 Implement Real CopilotKit Integration

**Priority**: HIGH - ChatPanel currently mocked

**Tasks**:

- Replace setTimeout mock with real API call
- Integrate with `/api/copilotkit` endpoint
- Handle streaming responses
- Add message persistence (localStorage or backend)
- Handle errors gracefully

**Files to modify**:

- `frontend/components/agents/ChatPanel.tsx`
- `frontend/lib/api.ts` (add chat API functions)

**Backend Integration**:

- Verify CopilotKit endpoint handles streaming
- Add session context to requests

### 2.2 Add Error Notifications & Recovery

**Priority**: HIGH - Users can't recover from errors

**Tasks**:

- Install toast notification library (react-hot-toast or sonner)
- Add error notifications for SSE failures
- Add retry mechanisms
- Show connection status indicator
- Add error recovery UI

**Files to create/modify**:

- `frontend/components/shared/Toast.tsx` (NEW)
- `frontend/components/shared/ConnectionStatus.tsx` (NEW)
- `frontend/hooks/useAgentEvents.ts` (add error state)
- All components using SSE (add error handling)

**Dependencies to add**:

- `react-hot-toast` or `sonner`

### 2.3 Improve Type Safety

**Priority**: MEDIUM - Reduces runtime errors

**Tasks**:

- Create type guard functions for event payloads
- Replace `as any` casts with proper type guards
- Add runtime validation for event payloads
- Improve type narrowing in components

**Files to create/modify**:

- `frontend/lib/typeGuards.ts` (NEW)
- `frontend/components/agents/TimelineItem.tsx`
- `frontend/components/agents/ToolInspector.tsx`
- `frontend/components/agents/WorkflowGraph.tsx`

**Example Type Guards**:

```typescript
export function isToolCallStartedPayload(
  payload: EventPayload
): payload is ToolCallStartedPayload {
  return 'tool_call_id' in payload && 'tool_name' in payload;
}
```

### 2.4 Add Security Fixes

**Priority**: MEDIUM - Prevents XSS vulnerabilities

**Tasks**:

- Install DOMPurify
- Sanitize JSON output before rendering
- Escape HTML in console logs
- Validate event payloads

**Files to modify**:

- `frontend/components/agents/TimelineItem.tsx`
- `frontend/components/agents/LiveConsole.tsx`
- `frontend/lib/sanitize.ts` (NEW)

**Dependencies to add**:

- `dompurify` and `@types/dompurify`

## Phase 3: Performance & UX (Week 3)

### 3.1 Add Event Virtualization

**Priority**: MEDIUM - Improves performance with many events

**Tasks**:

- Install react-window or @tanstack/react-virtual
- Implement virtualized timeline
- Implement virtualized console
- Add infinite scroll for loading historical events

**Files to modify**:

- `frontend/components/agents/AgentTimeline.tsx`
- `frontend/components/agents/LiveConsole.tsx`

**Dependencies to add**:

- `@tanstack/react-virtual` or `react-window`

### 3.2 Fix SplitPane Implementation

**Priority**: LOW - Minor UX issue

**Tasks**:

- Fix startPosRef calculation bug
- Improve resize handle responsiveness
- Add touch support for mobile
- Test edge cases

**Files to modify**:

- `frontend/components/layout/SplitPane.tsx`

### 3.3 Improve WorkflowGraph

**Priority**: LOW - Enhancement

**Tasks**:

- Add edge visualization for transitions
- Improve layout algorithm
- Add zoom/pan functionality
- Add node details on hover

**Files to modify**:

- `frontend/components/agents/WorkflowGraph.tsx`

## Phase 4: Testing & Quality (Week 4)

### 4.1 Add Unit Tests

**Priority**: MEDIUM - Ensures code quality

**Tasks**:

- Setup Jest + React Testing Library
- Test hooks (useAgentEvents)
- Test utility functions
- Test type guards
- Test error handling

**Files to create**:

- `frontend/__tests__/hooks/useAgentEvents.test.ts`
- `frontend/__tests__/lib/typeGuards.test.ts`
- `frontend/__tests__/lib/utils.test.ts`

**Test Coverage Goals**:

- Hooks: 80%+
- Utils: 90%+
- Type guards: 100%

### 4.2 Add Component Tests

**Priority**: MEDIUM - Prevents regressions

**Tasks**:

- Test shared components
- Test timeline components
- Test error states
- Test loading states

**Files to create**:

- `frontend/__tests__/components/shared/*.test.tsx`
- `frontend/__tests__/components/agents/*.test.tsx`

### 4.3 Add Integration Tests

**Priority**: LOW - Validates end-to-end flows

**Tasks**:

- Test SSE connection flow
- Test event streaming
- Test error recovery
- Test component interactions

**Files to create**:

- `frontend/__tests__/integration/sse.test.ts`
- `frontend/__tests__/integration/events.test.ts`

## Phase 5: Accessibility & Polish (Week 5)

### 5.1 Add Accessibility Features

**Priority**: MEDIUM - Required for production

**Tasks**:

- Add ARIA labels to all interactive elements
- Add keyboard navigation
- Add focus management
- Test with screen readers
- Add skip links

**Files to modify**:

- All component files

### 5.2 Extract Constants

**Priority**: LOW - Code quality

**Tasks**:

- Create constants file
- Extract magic numbers
- Extract timeout values
- Extract configuration

**Files to create**:

- `frontend/lib/constants.ts`

### 5.3 Add Documentation

**Priority**: LOW - Developer experience

**Tasks**:

- Add JSDoc comments to hooks
- Add component prop documentation
- Create component usage examples
- Update README

## Implementation Order

1. **Day 1-2**: Backend SSE endpoint (1.1)
2. **Day 3**: Fix hook dependencies (1.2)
3. **Day 4**: Add event limits (1.3)
4. **Day 5**: Fix SSE proxy (1.4)
5. **Week 2**: CopilotKit integration (2.1), Error handling (2.2)
6. **Week 3**: Type safety (2.3), Security (2.4), Performance (3.1-3.3)
7. **Week 4**: Testing (4.1-4.3)
8. **Week 5**: Accessibility (5.1), Polish (5.2-5.3)

## Success Metrics

- ✅ Backend SSE endpoint streams events correctly
- ✅ No memory leaks (events limited, proper cleanup)
- ✅ Error recovery works (users can retry failed connections)
- ✅ Type safety improved (no `as any` casts)
- ✅ Test coverage > 70%
- ✅ All critical bugs fixed
- ✅ Production-ready codebase

## Risk Mitigation

- **Backend SSE complexity**: Start with simple implementation, iterate
- **Performance issues**: Monitor memory usage, add limits early
- **Testing gaps**: Start with critical paths, expand coverage gradually
- **Breaking changes**: Use feature flags for major changes

### To-dos

- [ ] Create backend SSE endpoint at backend/app/api/routes/events.py and register in main.py
- [ ] Fix useAgentEvents hook dependency array and add useCallback for handlers
- [ ] Add MAX_EVENTS constant and implement event limiting in AgentTimeline and LiveConsole
- [ ] Update SSE proxy endpoint to properly handle backend stream and add Supabase fallback
- [ ] Replace ChatPanel mock with real CopilotKit API integration
- [ ] Add toast notifications, connection status indicator, and error recovery UI
- [ ] Create type guard functions and replace all as any casts
- [ ] Add DOMPurify for sanitization and escape HTML in console output
- [ ] Implement event virtualization for timeline and console using react-virtual
- [ ] Add unit tests for hooks, utils, and type guards with Jest + RTL
- [ ] Add component tests for shared and agent components
- [ ] Add ARIA labels, keyboard navigation, and focus management