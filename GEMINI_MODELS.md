# Gemini AI Models Guide

## 🤖 Available Gemini Models

Bot ini support semua model Gemini terbaru. Kamu bisa pilih model sesuai kebutuhan.

---

## 📊 Model Comparison

### 1. **gemini-2.0-flash-exp** ⚡ (RECOMMENDED)
- **Status:** Latest experimental model (October 2025)
- **Speed:** Fastest ⚡⚡⚡
- **Quality:** Excellent for most tasks
- **Cost:** Free tier: 1500 RPM (requests per minute)
- **Best for:** Production use, real-time responses
- **Default:** ✅ Ya, ini default model

**Pros:**
- Latest features & improvements
- Very fast response time
- Good quality output
- High rate limits

**Cons:**
- Experimental (API might change)
- Slightly less stable than production models

---

### 2. **gemini-1.5-flash** ⚡
- **Status:** Production stable
- **Speed:** Very fast ⚡⚡
- **Quality:** Great for general tasks
- **Cost:** Free tier: 1000 RPM
- **Best for:** General announcement generation

**Pros:**
- Production stable
- Fast response
- Good balance speed/quality
- Reliable

**Cons:**
- Slightly older than 2.0
- Lower context window than Pro

---

### 3. **gemini-1.5-pro** 🎯
- **Status:** Production stable
- **Speed:** Moderate ⚡
- **Quality:** Best quality, most capable
- **Cost:** Free tier: 360 RPM
- **Best for:** Complex prompts, nuanced content

**Pros:**
- Highest quality output
- Best reasoning & creativity
- Larger context window (2M tokens)
- Most capable model

**Cons:**
- Slower than Flash models
- Lower rate limits
- Overkill untuk simple tasks

---

### 4. **gemini-pro** (Legacy)
- **Status:** Legacy, will be deprecated
- **Speed:** Moderate
- **Quality:** Good
- **Cost:** Free tier: 60 RPM
- **Best for:** Backward compatibility

**Not recommended** - Use gemini-1.5-flash or newer instead.

---

## 🔧 How to Change Model

### Method 1: Environment Variable (Recommended)

Edit `.env` file:
```env
GEMINI_MODEL=gemini-2.0-flash-exp
```

Available options:
- `gemini-2.0-flash-exp` (Default, fastest, latest)
- `gemini-1.5-flash` (Stable, fast)
- `gemini-1.5-pro` (Best quality)
- `gemini-pro` (Legacy)

### Method 2: Code Level

Edit `services/gemini_service.py`:
```python
# Change default in initialize method
def initialize(self, model_name: str = 'your-model-here'):
```

---

## 📈 Rate Limits (Free Tier)

| Model | RPM | RPD | TPM |
|-------|-----|-----|-----|
| gemini-2.0-flash-exp | 1500 | 1500 | 4M |
| gemini-1.5-flash | 1000 | 1500 | 4M |
| gemini-1.5-pro | 360 | 10000 | 4M |
| gemini-pro | 60 | - | 32K |

**RPM** = Requests Per Minute  
**RPD** = Requests Per Day  
**TPM** = Tokens Per Minute

---

## 💡 Recommendations

### For Your Use Case (Announcement Bot):

**Best Choice:** `gemini-2.0-flash-exp` ✅

**Reasons:**
1. ⚡ Fast response time (important for good UX)
2. 🎯 High quality (good for creative announcements)
3. 🚀 Latest features & improvements
4. 📊 High rate limits (1500 RPM is more than enough)
5. 💰 Free tier is generous

**When to use gemini-1.5-pro:**
- Kamu butuh announcement yang SANGAT creative
- Complex prompts dengan banyak context
- Mau hasil terbaik & speed bukan prioritas

**When to use gemini-1.5-flash:**
- Mau yang paling stable (production critical)
- Don't want experimental features
- 1000 RPM is enough untuk kamu

---

## 🧪 Testing Different Models

Kamu bisa test & compare models:

1. **Test with gemini-2.0-flash-exp:**
   ```env
   GEMINI_MODEL=gemini-2.0-flash-exp
   ```
   Send: `/announce Test Channel Test [550]`

2. **Test with gemini-1.5-pro:**
   ```env
   GEMINI_MODEL=gemini-1.5-pro
   ```
   Send same command, compare quality

3. **Compare:**
   - Speed
   - Quality
   - Creativity
   - Style

---

## 🔍 Model Features Comparison

| Feature | 2.0 Flash Exp | 1.5 Flash | 1.5 Pro |
|---------|---------------|-----------|---------|
| Speed | Fastest | Very Fast | Moderate |
| Quality | Excellent | Great | Best |
| Context Window | 1M tokens | 1M tokens | 2M tokens |
| Multimodal | ✅ | ✅ | ✅ |
| Function Calling | ✅ | ✅ | ✅ |
| JSON Mode | ✅ | ✅ | ✅ |
| Safety Settings | ✅ | ✅ | ✅ |
| Grounding | ✅ | ✅ | ✅ |

---

## 📝 Example Output Quality

### Prompt:
```
Buatkan announcement untuk film Fight Club [550]
```

### gemini-2.0-flash-exp Output:
```
🎬 Film Klasik yang Gak Boleh Terlewatkan! 🎬

Fight Club (1999) sekarang available di Noobz Space! 

Starring Brad Pitt & Edward Norton dalam psychological thriller yang mind-bending dan penuh twist! 

⭐ Rating: 8.4/10
🎭 Genre: Drama, Thriller
💥 Tentang: Insomniac mencari pelarian dari hidup yang membosankan...

Siap punya pikiran lo ditiup? 💥

👉 Nonton sekarang: https://noobz.space/movie/550

#FightClub #BradPitt #PsychologicalThriller
```

### gemini-1.5-flash Output:
Similar quality, mungkin sedikit kurang creative.

### gemini-1.5-pro Output:
More detailed, lebih nuanced, tapi takes longer.

---

## 🛠️ Troubleshooting

### Error: "Model not found"

**Solution:**
Check model name spelling. Valid options:
- `gemini-2.0-flash-exp`
- `gemini-1.5-flash`
- `gemini-1.5-pro`
- `gemini-pro`

### Error: "Quota exceeded"

**Solutions:**
1. Wait for rate limit reset (1 minute)
2. Upgrade to paid tier
3. Use slower model (1.5-pro has higher daily limit)

### Error: "API key invalid"

**Solution:**
1. Check `.env` file has correct API key
2. Get new key from https://makersuite.google.com/app/apikey
3. Make sure no extra spaces in key

---

## 💰 Cost (Paid Tier)

If you need more than free tier:

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| 2.0 Flash Exp | $0.075 | $0.30 |
| 1.5 Flash | $0.075 | $0.30 |
| 1.5 Pro | $1.25 | $5.00 |

**For your bot:** Free tier is more than enough!

---

## 📚 Additional Resources

- **Gemini API Docs:** https://ai.google.dev/docs
- **Model Documentation:** https://ai.google.dev/models/gemini
- **API Pricing:** https://ai.google.dev/pricing
- **Rate Limits:** https://ai.google.dev/gemini-api/docs/rate-limits

---

## ✅ Current Configuration

Your bot is configured to use: **`gemini-2.0-flash-exp`** (Default)

To change:
```bash
nano .env
# Change GEMINI_MODEL=your-choice-here
# Save & restart bot
```

---

## 🎯 Bottom Line

**Stick with default `gemini-2.0-flash-exp`** ✅

It's:
- Latest & greatest
- Fast enough for real-time
- High quality output
- Free tier is generous
- Perfect untuk announcement bot

Only switch jika:
- You need absolute best quality → use 1.5-pro
- You need maximum stability → use 1.5-flash
- You hit rate limits → upgrade or use 1.5-pro (higher daily limit)

---

**Happy announcing! 🎉**
