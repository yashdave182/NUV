// Constants used across the application
export const CROPS = [
  { value: 'cotton', label: 'Cotton (Kapas)' },
  { value: 'groundnut', label: 'Groundnut (Mungfali)' },
  { value: 'wheat', label: 'Wheat (Gehun)' },
  { value: 'bajra', label: 'Bajra (Pearl Millet)' },
  { value: 'maize', label: 'Maize (Makka)' },
  { value: 'cumin', label: 'Cumin (Jeera)' },
  { value: 'castor', label: 'Castor (Arandi)' },
  { value: 'sesame', label: 'Sesame (Til)' },
  { value: 'tobacco', label: 'Tobacco (Tambakoo)' },
  { value: 'green_gram', label: 'Green Gram (Moong)' },
  { value: 'black_gram', label: 'Black Gram (Urad)' },
  { value: 'pigeon_pea', label: 'Pigeon Pea (Toor)' },
  { value: 'chilli', label: 'Chilli (Mirchi)' },
  { value: 'onion', label: 'Onion (Piyaz)' },
  { value: 'potato', label: 'Potato (Aloo)' },
  { value: 'banana', label: 'Banana (Kela)' },
  { value: 'papaya', label: 'Papaya (Papita)' },
  { value: 'mango', label: 'Mango (Aam)' },
]

export const SOIL_TYPES = [
  { value: 'black_cotton', label: 'Black Cotton Soil' },
  { value: 'alluvial', label: 'Alluvial Soil' },
  { value: 'red_loam', label: 'Red Loam' },
  { value: 'sandy_loam', label: 'Sandy Loam' },
  { value: 'clay', label: 'Clay' },
  { value: 'saline', label: 'Saline' },
  { value: 'alkaline', label: 'Alkaline' },
]

export const IRRIGATION_SOURCES = [
  { value: 'canal', label: 'Canal' },
  { value: 'borewell', label: 'Borewell' },
  { value: 'open_well', label: 'Open Well' },
  { value: 'pond', label: 'Pond' },
  { value: 'rainfed', label: 'Rainfed' },
  { value: 'drip', label: 'Drip Irrigation' },
  { value: 'sprinkler', label: 'Sprinkler' },
]

export const LANGUAGES = [
  'English', 'Hindi', 'Gujarati', 'Hinglish', 'Gujlish',
  'Marathi', 'Marathish', 'Tamil', 'Telugu', 'Kannada',
  'Punjabi', 'Bengali', 'Odia', 'Urdu',
]

export const STATES = [
  'Gujarat', 'Maharashtra', 'Rajasthan', 'Madhya Pradesh', 'Uttar Pradesh',
  'Punjab', 'Haryana', 'Bihar', 'West Bengal', 'Odisha',
  'Telangana', 'Andhra Pradesh', 'Karnataka', 'Tamil Nadu', 'Kerala',
]

export const SEASONS = [
  { value: 'kharif', label: 'Kharif (June – October)' },
  { value: 'rabi', label: 'Rabi (November – April)' },
  { value: 'zaid', label: 'Zaid (April – June)' },
  { value: 'perennial', label: 'Perennial' },
]

export const GROWTH_STAGES = [
  { value: 'germination', label: 'Germination' },
  { value: 'vegetative', label: 'Vegetative' },
  { value: 'flowering', label: 'Flowering' },
  { value: 'fruiting', label: 'Fruiting / Grain Filling' },
  { value: 'maturity', label: 'Maturity / Harvest' },
]

export const ANIMAL_TYPES = [
  { value: 'cow', label: 'Cow (Gai)' },
  { value: 'buffalo', label: 'Buffalo (Bhains)' },
  { value: 'goat', label: 'Goat (Bakri)' },
  { value: 'sheep', label: 'Sheep (Bhed)' },
  { value: 'poultry', label: 'Poultry (Murgi)' },
  { value: 'pig', label: 'Pig (Soor)' },
]

export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:7860'
