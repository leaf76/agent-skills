# Localization Reference

## Language Codes (ISO 639-1)

| Code | Language | Native Name |
|------|----------|-------------|
| en | English | English |
| zh-TW | Chinese (Traditional) | 繁體中文 |
| zh-CN | Chinese (Simplified) | 简体中文 |
| ja | Japanese | 日本語 |
| ko | Korean | 한국어 |
| es | Spanish | Español |
| fr | French | Français |
| de | German | Deutsch |
| pt | Portuguese | Português |
| ru | Russian | Русский |
| ar | Arabic | العربية |
| hi | Hindi | हिन्दी |

## Translation Guidelines

### Tone Adaptation

| Source Tone | English | 繁體中文 | 日本語 |
|-------------|---------|----------|--------|
| Casual | "Got it!" | 「收到！」 | 「了解！」 |
| Formal | "Understood." | 「已了解。」 | 「承知いたしました。」 |
| Friendly | "Hey there!" | 「嗨！」 | 「こんにちは！」 |

### UI Text Length

- Buttons: Keep under 2-3 words
- Labels: Keep concise, may need abbreviation
- Error messages: Full sentences allowed
- Tooltips: Medium length

### RTL Languages (Arabic, Hebrew)

- Reverse layout direction
- Mirror icons (arrows, progress bars)
- Keep numbers LTR

### Date/Time Formats

| Locale | Date | Time |
|--------|------|------|
| en-US | MM/DD/YYYY | 12-hour (AM/PM) |
| en-GB | DD/MM/YYYY | 24-hour |
| zh-TW | YYYY年MM月DD日 | 24-hour |
| ja | YYYY年MM月DD日 | 24-hour |
| de | DD.MM.YYYY | 24-hour |

### Number Formats

| Locale | Decimal | Thousands |
|--------|---------|-----------|
| en-US | . | , |
| de | , | . |
| fr | , | (space) |
| zh | . | , |

### Currency Symbols

| Currency | Symbol | Position |
|----------|--------|----------|
| USD | $ | Before |
| EUR | € | After (most EU) |
| GBP | £ | Before |
| JPY | ¥ | Before |
| TWD | NT$ | Before |
| CNY | ¥ | Before |

## Common Pitfalls

1. **String concatenation**: Avoid `"Hello " + name` - use placeholders
2. **Pluralization**: Use ICU MessageFormat or equivalent
3. **Gendered languages**: Account for grammatical gender
4. **Text expansion**: German/French can be 30% longer than English
5. **Character encoding**: Always use UTF-8
