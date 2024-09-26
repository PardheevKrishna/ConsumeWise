// app/dashboard/types/Analysis.ts

export interface Macronutrients {
  Carbohydrates?: {
    Good?: string[];
    Bad?: string[];
  };
  Proteins?: {
    Good?: string[];
    Bad?: string[];
  };
  Fats?: {
    Good?: string[];
    Bad?: string[];
  };
  Fiber?: {
    Good?: string[];
  };
}

export interface Micronutrients {
  Vitamins?: {
    Good?: string[];
    Deficient?: string[];
  };
  Minerals?: {
    Good?: string[];
    Deficient?: string[];
  };
}

export interface NutritionalAnalysis {
  Macronutrients?: Macronutrients;
  Micronutrients?: Micronutrients;
  HealthRisks?: string[];
  HealthBenefits?: string[];
}

export interface Analysis {
  NutritionalAnalysis?: NutritionalAnalysis;
  ProcessingLevel?: {
    Description?: string;
    Level?: "Low" | "Medium" | "High" | string;
    Good?: string[];
    Bad?: string[];
  };
  HarmfulIngredients?: {
    Ingredient: string;
    Reason: string;
  }[];
  DietCompliance?: {
    CompliantDiets?: string[];
    NonCompliantDiets?: string[];
    Reasons?: string;
  };
  DiabetesAllergenFriendly?: {
    IsSuitable: boolean;
    Reasons?: string;
    Allergens?: string[];
  };
  SustainabilityAndEthics?: {
    Sustainability?: string;
    EthicalConcerns?: string;
  };
  RecommendedAlternatives?: string[];
  RegulatoryCompliance?: {
    FSSAI: boolean | string;
    FDA: boolean | string;
    EFSA: boolean | string;
    OtherRegions?: string;
  };
  MisleadingClaims?: {
    Claim: string;
    Reason: string;
  }[];
  AlternativeHomeMadeProcedure?: {
    Ingredients?: string[];
    Steps?: string[];
  };
}
