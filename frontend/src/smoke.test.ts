import { describe, it, expect } from "vitest";
import { api } from "./services/api";

describe("Signify Frontend Architecture & Smoke Tests", () => {
  it("exports valid API endpoint methods", () => {
    expect(typeof api.getHealth).toBe("function");
    expect(typeof api.getManifest).toBe("function");
    expect(typeof api.listSigns).toBe("function");
    expect(typeof api.matchReversePhrase).toBe("function");
    expect(typeof api.classifyLandmarks).toBe("function");
    expect(typeof api.transcribeSpeech).toBe("function");
    expect(typeof api.synthesizeSpeech).toBe("function");
    expect(typeof api.translateText).toBe("function");
    expect(typeof api.orchestratorTransition).toBe("function");
    expect(typeof api.runAcceptanceTests).toBe("function");
  });
});

