from django.shortcuts import render
from .forms import factsForm
from .services import FactCheckerService
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import urllib, base64
import numpy as np
import pandas as pd

def home(request):
    """
    Main view for the Fact Checker application.
    Handles form submission, orchestrates the fact-checking service,
    and renders the result dashboard.
    # Trigger reload (Team Details Updated)
    """
    if request.method == 'POST':
        form = factsForm(request.POST)
        context = {'facts': form}

        if form.is_valid():
            user_query = form.cleaned_data['facts']
            
            # 1. Prepare Query
            search_query = FactCheckerService.get_date_range_query(user_query)
            
            # 2. Search Web
            top_urls = FactCheckerService.search_web(search_query)
            
            # 3. Scrape and Summarize
            summaries, valid_urls = FactCheckerService.scrape_and_summarize(top_urls, user_query)
            
            print(f"DEBUG VIEW: Summaries: {len(summaries)}, URLs: {len(valid_urls)}")

            # Logic Update: Only fail if absolutely NO data found
            if not summaries and not valid_urls:
                 # Try one last Hail Mary - Pass invalid URLs just to show *something* if search worked but scrape failed?
                 # ideally no, just show insufficient data.
                 # BUT, if we have URLs but no summaries, we should tell user "Found sources but couldn't verify content"
                 pass 

            if not summaries:
                 if valid_urls:
                     # We found URLs but failed to scrape. Partial success?
                     context['fact_check'] = "Found sources, but unable to analyze content deeply. Please check links below."
                     # Create a dummy summary so flow continues? No, wordcloud will fail.
                     # Let's create a dummy summary from titles or snippets if possible, but services doesn't return that.
                     # Fallback behavior:
                     pass
                 else:
                    context['fact_check'] = "Insufficient data found to verify."
                    return render(request, 'index.html', context)

            # 4. Calculate Similarity
            # If no summaries, this returns []
            similarities = FactCheckerService.check_similarity(user_query, summaries)
            
            # 5. Generate Word Cloud
            # 5. Visuals: Search Image -> Fallback to WordCloud
            news_image_url = FactCheckerService.fetch_image(user_query)
            uri = ""
            
            # If no image found, generate WordCloud
            if not news_image_url:
                try:
                    text = " "
                    if summaries:
                        sentences = np.array(summaries)
                        text = ' '.join(sentences)
                    
                    if not text.strip():
                        text = "No_Data_Found"
                        
                    wordcloud = WordCloud(width=800, height=500, background_color='#16191f', colormap='Set2').generate(text)
                    
                    # Convert plot to PNG image
                    fig = plt.figure(figsize=(10, 5), facecolor='#16191f')
                    plt.imshow(wordcloud)
                    plt.axis("off")
                    plt.tight_layout(pad=0)
                    
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
                    uri = urllib.parse.quote(image_base64)
                    plt.close(fig) 
                except Exception as wc_e:
                    print(f"WordCloud Error: {wc_e}")
                    uri = ""

            # 6. Determine Verdict
            if similarities:
                avg_similarity = np.mean(similarities)
                max_similarity = np.max(similarities)
                source_count = len(valid_urls)
                verdict = FactCheckerService.classify_verdict(avg_similarity, max_similarity, source_count, user_query)
            else:
                verdict = "Could not determine similarity."

            # 7. Prepare Results Table
            # Converting list of URLs to a HTML table for display
            results_df = pd.DataFrame(valid_urls, columns=['Source URLs'])
            results_table_html = results_df.to_html(classes='table table-striped', index=False)

            # Update Context
            context.update({
                'fine': results_table_html, 
                'fact_check': verdict,
                'news_image': news_image_url,
                'data': uri
            })

        return render(request, 'index.html', context)
    
    else:
        form = factsForm()
        return render(request, 'index.html', {'facts': form})

def about(request):
    """Renders the About page with team details."""
    return render(request, 'about.html')