#ifndef __CACHE_BLOCK_INFO_H__
#define __CACHE_BLOCK_INFO_H__

#include "fixed_types.h"
#include "cache_state.h"
#include "cache_base.h"
#include "epoch_manager.h" // Added by Kleber Kruger

class CacheBlockInfo
{
   public:
      enum option_t
      {
         PREFETCH,
         WARMUP,
         NUM_OPTIONS
      };

      static const UInt8 BitsUsedOffset = 3;  // Track usage on 1<<BitsUsedOffset granularity (per 64-bit / 8-byte)
      typedef UInt8 BitsUsedType;      // Enough to store one bit per 1<<BitsUsedOffset byte element per cache line (8 8-byte elements for 64-byte cache lines)

   // This can be extended later to include other information
   // for different cache coherence protocols
   private:
      IntPtr m_tag;
      CacheState::cstate_t m_cstate;
      UInt64 m_owner;
      BitsUsedType m_used;
      UInt8 m_options;  // large enough to hold a bitfield for all available option_t's
      UInt64 m_eid;     // Added by Kleber Kruger

      static const char* option_names[];

   public:
      CacheBlockInfo(IntPtr tag = ~0,
            CacheState::cstate_t cstate = CacheState::INVALID,
            UInt64 options = 0);
      virtual ~CacheBlockInfo();

      static CacheBlockInfo* create(CacheBase::cache_t cache_type);

      virtual void invalidate(void);
      virtual void clone(CacheBlockInfo* cache_block_info);

      bool isValid() const { return (m_tag != ((IntPtr) ~0)); }
      bool isDurty() const { return (m_cstate == CacheState::MODIFIED); } // Added by Kleber Kruger

      IntPtr getTag() const { return m_tag; }
      CacheState::cstate_t getCState() const { return m_cstate; }

      void setTag(IntPtr tag) { m_tag = tag; }
      void setCState(CacheState::cstate_t cstate) { 
         m_cstate = cstate;
         // Added by Kleber Kruger
         if (cstate == CacheState::MODIFIED) 
            m_eid = EpochManager::getGlobalSystemEID(); 
      }

      UInt64 getOwner() const { return m_owner; }
      void setOwner(UInt64 owner) { m_owner = owner; }

      UInt64 getEpochID() const { return m_eid; } // Added by Kleber Kruger

      bool hasOption(option_t option) { return m_options & (1 << option); }
      void setOption(option_t option) { m_options |= (1 << option); }
      void clearOption(option_t option) { m_options &= ~(UInt64(1) << option); }

      BitsUsedType getUsage() const { return m_used; };
      bool updateUsage(UInt32 offset, UInt32 size);
      bool updateUsage(BitsUsedType used);

      static const char* getOptionName(option_t option);
};

class CacheCntlr
{
   public:
      virtual bool isInLowerLevelCache(CacheBlockInfo *block_info) { return false; }
      virtual void incrementQBSLookupCost() {}
      virtual void checkpoint(CheckpointEvent::Type event_type) {} // Added by Kleber Kruger
};

#endif /* __CACHE_BLOCK_INFO_H__ */
