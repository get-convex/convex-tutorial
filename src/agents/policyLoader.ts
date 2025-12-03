// agents/policyLoader.ts

// Load the policy files (you'll need to serve these from your public folder)
export class PolicyLoader {
    private qPolicy: number[] | null = null;
    private mlePolicy: number[] | null = null;
    
    async loadPolicies() {
      try {
        // Load Q-learning policy
        const qResponse = await fetch('/policies/medium.policy');
        const qText = await qResponse.text();
        this.qPolicy = qText.trim().split('\n').map(Number);
        
        // Load MLE policy  
        const mleResponse = await fetch('/policies/mle_policy.txt');
        const mleText = await mleResponse.text();
        this.mlePolicy = mleText.trim().split('\n').map(Number);
        
        console.log('Policies loaded:', {
          qLength: this.qPolicy?.length,
          mleLength: this.mlePolicy?.length
        });
      } catch (error) {
        console.error('Failed to load policies:', error);
      }
    }
    
    getAction(playerType: string, stateId: number): number {
      // Map of action indices to game actions:
      // 0 = Draw
      // 1 = Play Skip
      // 2 = Play Attack
      // 3 = Play Favor
      // 4 = Play Nope
      // 5 = Play SeeFuture
      // 6 = Play Shuffle
      // 7 = Play Cat
      
      switch (playerType) {
        case 'qlearning':
          return this.qPolicy?.[stateId] ?? 0; // Default to draw if policy not loaded
        case 'mle':
          return this.mlePolicy?.[stateId] ?? 0;
        case 'random':
          return Math.floor(Math.random() * 8);
        case 'bayesian':
          // Simple Bayesian: prefer playing cards if available, otherwise draw
          return Math.random() > 0.5 ? Math.floor(Math.random() * 7) + 1 : 0;
        default:
          return 0; // Default to draw
      }
    }
  }