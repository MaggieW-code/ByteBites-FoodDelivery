// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useDebounce } from "../useDebounce";

describe("useDebounce", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  const setup = () =>
    renderHook(({ value }) => useDebounce(value, 250), {
      initialProps: { value: "" },
    });

  it("returns the initial value immediately", () => {
    const { result } = setup();
    expect(result.current).toBe("");
  });

  it("does not update before the delay", () => {
    const { result, rerender } = setup();
    rerender({ value: "sushi" });
    act(() => { vi.advanceTimersByTime(249); });
    expect(result.current).toBe("");
  });

  it("updates exactly at the delay", () => {
    const { result, rerender } = setup();
    rerender({ value: "sushi" });
    act(() => { vi.advanceTimersByTime(250); });
    expect(result.current).toBe("sushi");
  });

  it("restarts the timer on every change and keeps only the last value", () => {
    const { result, rerender } = setup();

    rerender({ value: "s" });
    act(() => { vi.advanceTimersByTime(200); });
    rerender({ value: "su" });
    act(() => { vi.advanceTimersByTime(200); });
    rerender({ value: "sus" });

    act(() => { vi.advanceTimersByTime(249); });
    expect(result.current).toBe("");

    act(() => { vi.advanceTimersByTime(1); });
    expect(result.current).toBe("sus");
  });

  it("does not update after unmount", () => {
    const { result, rerender, unmount } = setup();
    rerender({ value: "sushi" });
    unmount();
    act(() => { vi.advanceTimersByTime(500); });
    expect(result.current).toBe("");
  });
});
