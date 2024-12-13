// src/schemas.ts
import { z } from 'zod';

// Enums
export const PhaseEnum = z.enum([
  'Initialize',
  'Werewolf',
  'Prophet',
  'Witch',
  'Day',
  'Speak',
  'Vote',
  'End'
]);

// Base Schemas
export const RolesSchema = z.object({
  Werewolf: z.number().int().nonnegative(),
  Prophet: z.number().int().nonnegative(),
  Witch: z.number().int().nonnegative(),
  Villager: z.number().int().nonnegative(),
});

export const WitchConfigSchema = z.object({
  cure_count: z.number().int().nonnegative(),
  poison_count: z.number().int().nonnegative(),
});

export const BasePlayerSchema = z.object({
  index: z.string(),
  name: z.string().min(1),
  alive: z.boolean(),
});

export const PlayerSchema = BasePlayerSchema.extend({
  online: z.boolean(),
});

export const AIPlayerSchema = BasePlayerSchema;

export const PhaseTimerSchema = z.object({
  Initialize: z.number().int().positive(),
  Werewolf: z.number().int().positive(),
  Prophet: z.number().int().positive(),
  Witch: z.number().int().positive(),
  Day: z.number().int().positive(),
  Speak: z.number().int().positive(),
  Vote: z.number().int().positive(),
  End: z.number().int().positive(),
});

// Main Game Schema
export const GameDataSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1),
  description: z.string(),
  max_players: z.number().int().positive(),
  night_count: z.number().int().nonnegative(),
  roles: RolesSchema,
  witch_config: WitchConfigSchema,
  players: z.record(z.string(), PlayerSchema),
  ai_players: z.record(z.string(), AIPlayerSchema),
  current_phase: PhaseEnum,
  phase_timer: PhaseTimerSchema,
});

// Type exports
export type Phase = z.infer<typeof PhaseEnum>;
export type Roles = z.infer<typeof RolesSchema>;
export type WitchConfig = z.infer<typeof WitchConfigSchema>;
export type BasePlayer = z.infer<typeof BasePlayerSchema>;
export type Player = z.infer<typeof PlayerSchema>;
export type AIPlayer = z.infer<typeof AIPlayerSchema>;
export type PhaseTimer = z.infer<typeof PhaseTimerSchema>;
export type GameData = z.infer<typeof GameDataSchema>;

// Validation helper functions
export const validateGame = (data: unknown) => {
  try {
    return {
      success: true,
      data: GameDataSchema.parse(data)
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        errors: error.errors.map(err => ({
          path: err.path.join('.'),
          message: err.message
        }))
      };
    }
    return {
      success: false,
      errors: [{ path: '', message: 'Unknown error' }]
    };
  }
};

// Optional: Partial schemas for updates
export const PartialGameSchema = GameDataSchema.partial();
export type PartialGame = z.infer<typeof PartialGameSchema>;