import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { text } = await req.json();

    if (!text || text.length < 10) {
      return NextResponse.json({ error: 'Please provide more text to analyze.' }, { status: 400 });
    }

    const redFlags = [
      'shocking', 'they don\'t want you to know', 'miracle', 'exposed', 
      'mainstream media won\'t tell', '100% proof', 'conspiracy', 'secret cure',
      'you won\'t believe', 'elite', 'hoax', 'banned', 'urgent'
    ];

    const lowerText = text.toLowerCase();
    let score = 0;
    const detectedFlags: string[] = [];

    redFlags.forEach((word) => {
      if (lowerText.includes(word)) {
        score += 15;
        detectedFlags.push(word);
      }
    });

    const uppercaseCount = text.replace(/[^A-Z]/g, "").length;
    const uppercaseRatio = uppercaseCount / text.length;
    if (uppercaseRatio > 0.25) {
      score += 25;
      detectedFlags.push('Excessive Caps / Panic Framing');
    }

    const exclamationMatches = text.match(/!{2,}/g);
    if (exclamationMatches) {
      score += 15;
      detectedFlags.push('Multiple Exclamation Marks');
    }

    const finalRiskScore = Math.min(Math.max(score + 10, 5), 95);

    let rating = 'Credible / Balanced';
    if (finalRiskScore > 40) rating = 'Suspicious / Sensationalized';
    if (finalRiskScore > 75) rating = 'High Probability of Misinformation';

    return NextResponse.json({
      riskScore: finalRiskScore,
      rating,
      triggers: detectedFlags,
      summary: `Scanned text for behavior patterns and found ${detectedFlags.length} emotional manipulation vectors.`
    });

  } catch (error) {
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
